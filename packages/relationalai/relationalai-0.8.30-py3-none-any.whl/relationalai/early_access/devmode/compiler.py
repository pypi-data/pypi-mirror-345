from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, cast

from relationalai.early_access.metamodel import ir, compiler as c, visitor as v, factory as f, builtins, types, rewrite as rw, typer
from relationalai.early_access.metamodel.util import FrozenOrderedSet, OrderedSet, frozen, ordered_set, filter_by_type
from relationalai.early_access.devmode import sql, rewrite

class Compiler(c.Compiler):
    def __init__(self):
        super().__init__([
            rw.RewriteListTypes(),
            rw.GCUnusedRelations(),
            typer.Checker(),
            typer.Typer(),
            rw.GCUnusedRelations(),
            rewrite.Denormalize()
            # group updates
            # compute SCCs, use Sequence to denote their order
        ])

    def do_compile(self, model: ir.Model, options:dict={}) -> str:
        # print()
        # print(model)
        v = ModelToSQL()
        model.accept(v)
        # print()
        # print(v.to_sql_code())
        return v.to_sql_code()


@dataclass
class ModelToSQL(v.Visitor):
    """ Generates SQL from an IR Model, assuming the compiler rewrites were done. """

    # the resulting statements
    statements: list[sql.Node] = field(default_factory=list)

    #--------------------------------------------------
    # Public API
    #--------------------------------------------------

    def to_sql_code(self):
        return "\n".join(str(s) for s in self.statements)


    #--------------------------------------------------
    # Visitor Implementation
    #--------------------------------------------------

    def visit(self, n: ir.Node, parent: Optional[ir.Node]):
        # declare tables when visiting the relation list in the model
        if isinstance(n, ir.Relation) and isinstance(parent, ir.Model) and not builtins.is_builtin(n):
            self._create_table(n)
            return False

        if isinstance(n, ir.Union):
            # currently treat as a recursive view
            self._create_recursive_view(n)
            return False

        if isinstance(n, ir.Logical) and isinstance(parent, ir.Logical):
            # currently only take the logical tasks under the top-level logical
            self._create_statement(n)
            return False
        return True

    #--------------------------------------------------
    # SQL Generation
    #--------------------------------------------------
    def _create_table(self, r: ir.Relation):
        self.statements.append(sql.CreateTable(
            sql.Table(r.name,
                list(map(lambda f: sql.Column(f.name, self._convert_type(f.type)), r.fields))
            )))

    def _create_recursive_view(self, union: ir.Union):
        assert len(union.tasks) == 2
        assert isinstance(union.tasks[0], ir.Logical)
        assert isinstance(union.tasks[1], ir.Logical)

        def make_case_select(logical: ir.Logical):
            # TODO - improve the typing info to avoid these casts
            lookups = cast(list[ir.Lookup], filter_by_type(logical.body, ir.Lookup))
            # TODO - assuming a single update per case
            update = v.collect_by_type(ir.Update, logical).some()

            # TODO - rewriting references to the view, to use the CTE instead, with _rec
            new_lookups = []
            for lookup in lookups:
                if lookup.relation == update.relation:
                    new_lookups.append(f.lookup(
                        ir.Relation(f"{lookup.relation.name}_rec", lookup.relation.fields, frozen(), frozen()), lookup.args, lookup.engine))
                else:
                    new_lookups.append(lookup)

            aliases = []
            for i, arg in enumerate(update.args):
                aliases.append((update.relation.fields[i].name, arg))
            return self._make_select(new_lookups, aliases)

        # get a representative update
        update = v.collect_by_type(ir.Update, union).some()

        # TODO - maybe this should be more like INSERT INTO a table than a view?
        self.statements.append(sql.CreateView(update.relation.name,
            sql.CTE(True, f"{update.relation.name}_rec", [f.name for f in update.relation.fields], [
                make_case_select(cast(ir.Logical, union.tasks[0])),
                make_case_select(cast(ir.Logical, union.tasks[1]))
            ]))
        )


    def _create_statement(self, logical: ir.Logical):

        # TODO - improve the typing info to avoid these casts
        lookups = cast(list[ir.Lookup], filter_by_type(logical.body, ir.Lookup))
        updates = cast(list[ir.Update], filter_by_type(logical.body, ir.Update))
        outputs = cast(list[ir.Output], filter_by_type(logical.body, ir.Output))

        # TODO - this is simplifying soooo much :crying_blood:
        if updates and not lookups:
            # TODO: this is assuming that the updates are all static values
            # insert static values: INSERT INTO ... VALUES ...
            for u in updates:
                r = u.relation
                tuples = self._get_tuples(logical, u)
                for tuple in tuples:
                    self.statements.append(
                        sql.Insert(r.name, [f.name for f in r.fields], tuple, None)
                    )
        elif updates and lookups:
            # insert values that match a query: INSERT INTO ... SELECT ... FROM ... WHERE ...
            for u in updates:
                r = u.relation
                aliases = []
                for i, arg in enumerate(u.args):
                    aliases.append((r.fields[i].name, arg))

                self.statements.append(
                    sql.Insert(r.name,
                               [f.name for f in r.fields], [],
                               self._make_select(lookups, aliases)
                    )
                )
        elif outputs and lookups:
            # output a query: SELECT ... FROM ... WHERE ...
            aliases = []
            for o in outputs:
                aliases.extend(o.aliases)
            self.statements.append(self._make_select(lookups, aliases))
            pass
        else:
            raise Exception(f"Cannot create SQL statement for:\n{logical}")



    def _make_select(self, lookups: list[ir.Lookup], outputs: list[Tuple[str, ir.Value]]) -> sql.Select:
        table_lookups = filter(lambda t: not builtins.is_builtin(t.relation), lookups)
        froms = []
        sql_vars: dict[ir.Lookup, str] = dict() # one var per table lookup
        var_column: dict[Tuple[ir.Var, ir.Lookup], ir.Field] = dict()
        var_sql_var: dict[ir.Var, str] = dict()
        var_lookups: dict[ir.Var, OrderedSet[ir.Lookup]] = dict()
        i = 0
        for lookup in table_lookups:
            varname = f"v{i}"
            i += 1
            froms.append(sql.From(lookup.relation.name, varname))
            sql_vars[lookup] = varname
            j = 0
            for arg in lookup.args:
                if isinstance(arg, ir.Var):
                    var_column[arg, lookup] = lookup.relation.fields[j]
                    var_sql_var[arg] = varname
                    if arg not in var_lookups:
                        var_lookups[arg] = ordered_set()
                    var_lookups[arg].add(lookup)
                j += 1

        computed_outputs: dict[ir.Var, str] = dict()

        wheres: list[sql.Expr] = []
        # uses of built-in expressions
        def reference(v):
            if isinstance(v, ir.Var):
                # TODO - assuming the built-in reference was grounded elsewhere
                lookup = var_lookups[v].some()
                return f"{var_sql_var[v]}.{var_column[(v, lookup)].name}"
            else:
                # assuming a literal
                return str(v)
        for lookup in filter(lambda t: builtins.is_builtin(t.relation), lookups):
            # TODO - assuming infix binary or ternary operators here
            lhs = reference(lookup.args[0])
            rhs = reference(lookup.args[1])
            if len(lookup.args) == 3 and isinstance(lookup.args[2], ir.Var):
                # TODO - assuming that the computed value is going to be returned, which is obviously generally wrong
                computed_outputs[lookup.args[2]] = f"{lhs} {lookup.relation.name} {rhs}"
            else:
                wheres.append(sql.Terminal(f"{lhs} {lookup.relation.name} {rhs}"))
        # if there are 2 lookups for the same variable, we need a join
        for arg, lookup_set in var_lookups.items():
            if len(lookup_set) > 1:
                refs = [f"{sql_vars[lu]}.{var_column[cast(ir.Var, lu.args[0]), lu].name}" for lu in lookup_set]
                # join variable references pairwise (e.g. "x.id = y.id AND y.id = z.id")
                for lhs, rhs in zip(refs, refs[1:]):
                    wheres.append(sql.Terminal(f"{lhs} = {rhs}"))

        # conjunction of wheres
        if len(wheres) == 0:
            where = None
        elif len(wheres) == 1:
            where = sql.Where(wheres[0])
        else:
            where = sql.Where(sql.And(wheres))

        # finally, compute what the select will return
        vars = []
        for alias, var in outputs:
            if isinstance(var, ir.Var):
                if var in var_lookups:
                    lookup = var_lookups[var].some()
                    vars.append(sql.VarRef(sql_vars[lookup], var_column[var, lookup].name, alias))
                elif var in computed_outputs:
                    # TODO - abusing VarRef.name here, it's actually an expression here. Fix it!
                    vars.append(sql.VarRef(computed_outputs[var], None, alias))
                else:
                    # TODO - abusing even more here, because var is a value!
                    vars.append(sql.VarRef(str(var), None, alias))


        return sql.Select(False, vars, froms, where)



    def _get_tuples(self, logical: ir.Logical, u: ir.Update):
        """
        Get a list of tuples to perform this update.

        This function traverses the update args, assuming they contain only static values or
        variables bound to a construct task, and generates a list of tuples to insert. There
        may be multiple tuples because arguments can be lists of values bound to a field
        whose role is multi.
        """
        # TODO - this only works if the variable is bound to a Construct task, we need a
        # more general approach.
        values = []
        for a in u.args:
            if isinstance(a, ir.Var):
                for t in logical.body:
                    if isinstance(t, ir.Construct) and t.id_var == a:
                        values.append(f"hash({', '.join([self._convert_value(v) for v in t.values])})")
                        break
            elif isinstance(a, FrozenOrderedSet):
                values.append(frozen(*[self._convert_value(v) for v in a]))
            else:
                values.append(self._convert_value(a))
        return self._product(values)

    def _product(self, values):
        """ Compute a cartesian product of values when the value is a FrozenOrderedSet. """
        # TODO - some pass needs to check that this is correct, i.e. that we are using a
        # FrozenOrderedSet only if the field is of role multi.
        tuples = [[]]
        for value in values:
            if isinstance(value, FrozenOrderedSet):
                tuples = [prev + [element] for prev in tuples for element in value]
            else:
                tuples = [prev + [value] for prev in tuples]
        return tuples

    def _convert_value(self, v) -> str:
        """ Convert the literal value in v to a SQL value."""
        if isinstance(v, str):
            return f"'{v}'"
        if isinstance(v, ir.ScalarType):
            return f"'{v.name}'"
        if isinstance(v, ir.Literal):
            return self._convert_value(v.value)
        return v

    BUILTIN_CONVERSION = {
        "Hash": "UBIGINT",
        "String": "TEXT",
        "Number": "DOUBLE",
        "Int": "INT",
        "Decimal": "DECIMAL(13, 2)",
        "Bool": "BOOLEAN"
    }
    def _convert_type(self, t: ir.Type) -> str:
        """ Convert the type t into the equivalent SQL type."""
        if isinstance(t, ir.SetType):
            return self._convert_type(t.element_type)

        # entities become HUGEINT
        if not types.is_builtin(t):
            return "HUGEINT"

        # convert known builtins
        if isinstance(t, ir.ScalarType) and t.name in self.BUILTIN_CONVERSION:
            return self.BUILTIN_CONVERSION[t.name]
        raise Exception(f"Unknown built-in type: {t}")
