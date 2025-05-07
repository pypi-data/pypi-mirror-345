from __future__ import annotations
from typing import Any, Iterable, Sequence as PySequence, cast, Tuple, Union
from dataclasses import dataclass, field

from relationalai.early_access.metamodel import ir, compiler as c, builtins as bt, types, visitor, typer, helpers

from relationalai.early_access.metamodel.rewrite import Splinter, RewriteListTypes, GCUnusedRelations
from relationalai.early_access.metamodel.visitor import ReadWriteVisitor
from relationalai.early_access.metamodel.util import OrderedSet, group_by, NameCache

from relationalai.early_access.rel import rel, rel_utils as u, rewrite


#--------------------------------------------------
# Compiler
#--------------------------------------------------

class Compiler(c.Compiler):
    def __init__(self):
        super().__init__([
            RewriteListTypes(),
            GCUnusedRelations(),
            typer.Checker(),
            typer.Typer(),
            GCUnusedRelations(),
            rewrite.ExtractCommon(),
            rewrite.Flatten(),
            rewrite.QuantifyVars(),
            Splinter()
        ])
        self.model_to_rel = ModelToRel()

    def do_compile(self, model: ir.Model, options:dict={}) -> str:
        return str(self.model_to_rel.to_rel(model, options=options))


@dataclass
class ModelToRel:
    """ Generates Rel from an IR Model, assuming the compiler rewrites were done. """

    relation_name_cache: NameCache = field(default_factory=NameCache)
    rule_name_cache: NameCache = field(default_factory=NameCache)


    #--------------------------------------------------
    # Public API
    #--------------------------------------------------

    def to_rel(self, model: ir.Model, options:dict = {}) -> rel.Program:
        self._register_external_relations(model)
        if options.get("no_declares"):
            return rel.Program(tuple(self._generate_rules(model)))
        else:
            return rel.Program(tuple([
                *self._generate_declares(model),
                *self._generate_rules(model),
            ]))

    #--------------------------------------------------
    # Top level handlers
    #--------------------------------------------------

    def _generate_declares(self, m: ir.Model) -> list[rel.Declare]:
        """
        Generate declare statements for relations declared by the model and:
            - not built-ins
            - not used as an annotation
            - not annotated as external
            - do not start with ^ (for hardcoded Rel constructors)
            - and are never the target of an update
        """
        rw = ReadWriteVisitor()
        m.accept(rw)

        root = cast(ir.Logical, m.root)

        annotations = [anno.relation for anno in visitor.collect_by_type(ir.Annotation, m.root)]
        reads = m.relations - rw.writes(root) - bt.builtin_relations - annotations
        reads = list(filter(lambda r: not r.name.startswith('^') and not helpers.is_external(r), reads))

        declares: list[rel.Declare] = []
        for r in reads:
            if r.name in rel.infix or r.name in u.OPERATORS:
                continue
            # In case parameter name starts with ':' use its name instead of type name
            def requires_name(field: ir.Field):
                if isinstance(field.type, ir.ScalarType):
                    t = field.type
                    if t == types.Symbol:
                        return rel.MetaValue(field.name[1:])
                    else:
                        return rel.Var(name=u.sanitize(field.name.lower()), type=u.rel_typename(t))
                else:
                    return rel.Var('_')
            head = tuple([requires_name(f) for f in r.fields])

            # Example: declare test(:a, _x0 in Int, _x1 in String) requires true
            declares.append(rel.Declare(
                rel.atom(self._relation_name(r), head),
                True  # `requires true` does not generate any constraints, that affects performance on the RAI side
            ))
        return declares

    def _generate_rules(self, m: ir.Model) -> list[Union[rel.Def, rel.RawSource]]:
        """ Generate rules for the root of this model.

        Assumes the model already was processed such that it contains a root Logical with
        children that are also Logical tasks representing the rules to generate.
        """
        rules: list[Union[rel.Def, rel.RawSource]] = []
        root = cast(ir.Logical, m.root)
        for child in root.body:
            rules.extend(self._generate_rule(cast(ir.Logical, child)))
        return rules

    def _generate_rule(self, rule: ir.Logical) -> list[Union[rel.Def, rel.RawSource]]:
        """ Generate rules for a nested Logical in a model.

        This is for a top-level Logical, under the root Logical.
        """
        # reset the name cache for each rule
        self.rule_name_cache = NameCache()
        effects, other, aggregates = self._split_tasks(rule.body)
        if not effects:
            raise Exception("Cannot create top-level rule without effects.")

        elif len(effects) == 1:
            # a single effect with a body becomes a single rule
            effect = effects[0]

            # deal with raw sources
            if isinstance(effect, ir.Update) and effect.relation == bt.raw_source:
                # TODO: remove this once the type checker checks this.
                assert(len(effect.args) == 2 and isinstance(effect.args[0], str) and isinstance(effect.args[1], str))
                if effect.args[0] != "rel":
                    return []
                return [rel.RawSource(cast(str, effect.args[1]))]
            else:
                name = self._effect_name(effect)
                annos = effect.annotations if isinstance(effect, ir.Update) else []
                return [rel.Def(
                    self._effect_name(effect),
                    self._effect_args(effect),
                    self.generate_logical_body(other, aggregates),
                    self.generate_annotations(annos)
                )]
        else:
            # currently we can only deal with multiple effects if they are all updates with
            # no body, which is the pattern for inserting hardcoded data.
            if other or aggregates:
                raise NotImplementedError("Body in logical task with multiple effects.")
            if any(isinstance(effect, ir.Output) for effect in effects):
                raise NotImplementedError("Output in logical task with multiple effects.")
            sample = cast(ir.Update, effects[0]).effect
            if any(cast(ir.Update, effect).effect != sample for effect in effects):
                raise NotImplementedError("Different types of effects in logical task.")

            # Group updates by relation name
            relation_groups = group_by(cast(list[ir.Update], effects), lambda e: self._relation_name(e.relation))

            # Process each relation group
            defs = []
            for name, updates in relation_groups.items():
                effects_to_union = []
                for update in updates:
                    update_args = self._effect_args(update)
                    if update_args:
                        defs.append(
                            rel.Def(
                                name,
                                update_args,
                                True,
                                self.generate_annotations(update.annotations)
                            )
                        )
                    else:
                        effects_to_union.append(update)

                if effects_to_union:
                    bodies = []
                    for update in effects_to_union:
                        bodies.append(self.handle(update))
                    update = updates.some()
                    defs.append(
                        rel.Def(
                            name,
                            self._effect_args(update),
                            rel.Union(tuple(bodies)),
                            self.generate_annotations(update.annotations)
                        )
                    )
            return defs

    def generate_logical_body(self, other, aggregates):
        """ Generate the body of a rule for a Logical that contains these aggregates and
        other tasks (i.e. no effects)."""

        if not aggregates:
            # no aggregates, just return an expression for the body
            return self.generate_body_expr(other)
        else:
            # push the body into the aggregates; this assumes a rewrite pass already
            # prepared the body to contain only what's needed by the aggregates
            exprs = []
            for agg in aggregates:
                # TODO - some aggregations have multiple results, they need special handling
                result = self.handle_var(cast(ir.Var, agg.args[-1]))

                # head in the relational abstraction are agg's "projection" + "over"
                abs_head = list(agg.projection)
                if len(agg.args) > 1: # e.g. count does not have "over"
                    over = agg.args[-2]
                    if isinstance(over, ir.Var):
                        abs_head.append(over)
                    else:
                        abs_head.append(self.handle(over))

                abstraction = rel.RelationalAbstraction(
                    self.handle_list(tuple(abs_head)),
                    self.generate_body_expr(other)
                )
                exprs.append(rel.atom(
                    u.rel_operator(agg.aggregation.name),
                    tuple([ abstraction, result ])
                ))
            return exprs[0] if len(exprs) == 1 else rel.create_and(exprs)

    def generate_body_expr(self, tasks: list[ir.Task]):
        """ Helper to generate the an expression from the tasks, wrapping in Ands if necessary. """
        if not tasks:
            return True
        elif len(tasks) == 1:
            return self.handle(tasks[0])
        else:
            return rel.create_and([self.handle(b) for b in tasks])

    #--------------------------------------------------
    # IR handlers
    #--------------------------------------------------

    def handle(self, n: Union[ir.Value, ir.Node]):
        if isinstance(n, ir.Node):
            handler = getattr(self, f"handle_{n.kind}", None)
            if handler:
                return handler(n)
            else:
                raise Exception(f"Rel Compiler handler for '{n.kind}' node not implemented.")
        else:
            # TODO - every call to handle_value with None needs to get a type wired
            return self.handle_value(None, n)

    def handle_list(self, n):
        return tuple([self.handle(x) for x in n])

    def handle_value(self, type: Any, value: Any) -> Union[rel.Primitive, rel.MetaValue]:
        if type == types.Symbol:
            return rel.MetaValue(value)
        else:
            return value

    def handle_value_list(self, types, values) -> Tuple[Union[rel.Primitive, rel.MetaValue], ...]:
        return tuple([self.handle_value(t, v) for t, v in zip(types, values)])

    #
    # DATA MODEL
    #
    def handle_scalartype(self, n: ir.ScalarType):
        return n.name
    # TODO - what to generate for other kinds of types?




    #
    # TASKS
    #
    def handle_logical(self, n: ir.Logical) -> rel.Expr:
        # Generate nested expressions for a nested logical
        effects, other, aggregates = self._split_tasks(n.body)
        if effects:
            raise Exception("Cannot process nested logical with effects.")
        return self.generate_logical_body(other, aggregates)

    def handle_union(self, n: ir.Union) -> rel.Expr:
        # Generate nested expressions for a nested logical
        body:list[rel.Expr] = []
        for t in n.tasks:
            body.append(self.handle(t))
        return rel.Or(OrderedSet.from_iterable(body))

    #
    # LOGICAL QUANTIFIERS
    #
    def handle_not(self, n: ir.Not):
        return rel.Not(self.handle(n.task))

    def handle_exists(self, n: ir.Exists):
        vars = self._remove_wildcards(n.vars)
        if vars:
            return rel.Exists(
                self.handle_vars(vars),
                self.handle(n.task)
            )
        else:
            # all vars are wildcards, no need for exists
            return self.handle(n.task)

    #
    # ITERATION
    #

    #
    # RELATIONAL OPERATIONS
    #

    def handle_vars(self, vars: Tuple[ir.Var, ...]):
        return tuple([self.handle_var(v) for v in vars])

    def handle_var(self, n: ir.Var):
        if n.name == "_" or n.name.startswith(':'):
            return rel.Var(n.name)
        else:
            return rel.Var(f"_{self._var_name(n)}")

    def handle_literal(self, n: ir.Literal):
        return self.handle_value(n.type, n.value)

    def handle_data(self, n: ir.Data):
        return rel.Atom(rel.Union(tuple([self.handle(d) for d in n])), tuple([self.handle(d) for d in n.vars]))

    def generate_annotations(self, annos: Iterable[ir.Annotation]):
        """ Helper to cast the handling of ir.Annotations into a tuple of rel.Annotations. """
        return cast(Tuple[rel.Annotation, ...], self.handle_list(annos))

    def handle_annotation(self, n: ir.Annotation):
        return rel.Annotation(
            n.relation.name,
            self.handle_value_list([f.type for f in n.relation.fields], n.args)
        )

    def handle_update(self, n: ir.Update):
        return rel.atom(
            self._relation_name(n.relation),
            self.handle_list(n.args)
        )

    def handle_lookup(self, n: ir.Lookup):
        # only translate names to Rel operators if the relation is a built-in
        name = u.rel_operator(self._relation_name(n.relation)) if bt.is_builtin(n.relation) else self._relation_name(n.relation)
        return rel.atom(
            name,
            self.handle_list(n.args)
        )

    def handle_construct(self, n: ir.Construct):
        args = [self.handle(v) for v in n.values] + [self.handle(n.id_var)]
        return rel.atom("rel_primitive_hash_tuple_uint128", tuple(args))

    def handle_aggregate(self, n: ir.Aggregate):
        # TODO: this is very incorrect
        args = n.projection + n.group + n.args
        args = [self.handle(a) for a in args]
        return rel.atom(u.rel_operator(n.aggregation.name), tuple(args))


    #--------------------------------------------------
    # Helpers
    #--------------------------------------------------

    def _relation_name(self, relation: ir.Relation):
        if helpers.is_external(relation):
            return relation.name
        else:
            return self.relation_name_cache.get_name(relation.id, relation.name)

    def _var_name(self, var: ir.Var):
        if var.name == "_":
            return "_"
        return self.rule_name_cache.get_name(var.id, u.sanitize(var.name.lower()))

    def _remove_wildcards(self, vars: tuple[ir.Var, ...]):
        return tuple(filter(lambda v: v.name != "_", vars))

    def _register_external_relations(self, model: ir.Model):
        # force all external relations to get a name in the cache, so that internal relations
        # cannot use those names in _relation_name
        for r in model.relations:
            if helpers.is_external(r):
                self.relation_name_cache.get_name(r.id, r.name)

    def _split_tasks(self, tasks: PySequence[ir.Task]) -> tuple[list[ir.Task], list[Union[ir.Update, ir.Output]], list[ir.Aggregate]]:
        effects = []
        aggregates = []
        other_body = []
        for task in tasks:
            if isinstance(task, (ir.Update, ir.Output)):
                effects.append(task)
            elif isinstance(task, ir.Aggregate):
                aggregates.append(task)
            else:
                other_body.append(task)
        return effects, other_body, aggregates


    def _effect_name(self, n: ir.Task):
        if isinstance(n, ir.Output):
            return "output"
        elif isinstance(n, ir.Update):
            return self._relation_name(n.relation)
        else:
            raise Exception(f"Cannot retrieve effect name from node {type(n)}")

    def _effect_args(self, n: ir.Task):
        if isinstance(n, ir.Output):
            # TODO - deal with output aliases
            args = []
            for _, v in n.aliases:
                args.append(self.handle(v))
            return tuple(args)
        elif isinstance(n, ir.Update):
            args = []
            for a in n.args:
                args.append(self.handle(a))
            return tuple(args)
        else:
            raise Exception(f"Cannot retrieve effect params from node {type(n)}")
