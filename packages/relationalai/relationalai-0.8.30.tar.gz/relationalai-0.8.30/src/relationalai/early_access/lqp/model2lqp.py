from relationalai.early_access.metamodel.util import NameCache
from relationalai.early_access.lqp.validators import assert_valid_input, assert_valid_update
from relationalai.early_access.metamodel import ir, builtins as rel_builtins
from relationalai.early_access.lqp import ir as lqp
from relationalai.early_access.lqp.hash_utils import lqp_hash
from relationalai.early_access.lqp.primitives import relname_to_lqp_name, lqp_operator
from relationalai.early_access.lqp.types import meta_type_to_lqp, type_from_constant, type_from_term
from relationalai.early_access.lqp.constructors import mk_and, mk_exists, mk_or

from typing import Tuple, cast

class DebuggingCtx:
    """ Extra information only used for debugging. """
    def __init__(self, id_to_orig_name: dict[lqp.RelationId, str]):
       self.id_to_orig_name = id_to_orig_name

class TranslationCtx:
    def __init__(self, model):
        # TODO: comment these fields
        # TODO: should we have a pass to rename variables instead of this?
        self.var_name_cache = NameCache()
        self.id_to_orig_name = {}
        self.output_ids = []

    def debug_ctx(self) -> DebuggingCtx:
        return DebuggingCtx(self.id_to_orig_name)

""" Main access point. Converts the model IR to an LQP program. """
def to_lqp(model: ir.Model) -> Tuple[lqp.LqpProgram, DebuggingCtx]:
    assert_valid_input(model)
    ctx = TranslationCtx(model)
    program = _translate_to_program(ctx, model)
    debugging_ctx = ctx.debug_ctx()
    return (program, debugging_ctx)

def _translate_to_program(ctx: TranslationCtx, model: ir.Model) -> lqp.LqpProgram:
    decls: list[lqp.Declaration] = []
    outputs: list[Tuple[str, lqp.RelationId]] = []

    # LQP only accepts logical tasks
    # These are asserted at init time
    root = cast(ir.Logical, model.root)

    seen_rids = set()
    for subtask in root.body:
        assert isinstance(subtask, ir.Logical)
        decl = _translate_to_decl(ctx, subtask)

        assert isinstance(decl, lqp.Def), "we dont do loops yet m8"
        decls.append(decl)

        rid = decl.name
        assert rid not in seen_rids, f"duplicate relation id: {rid}"
        seen_rids.add(rid)

    for output_id in ctx.output_ids:
        assert isinstance(output_id, lqp.RelationId)
        outputs.append(("output", output_id))

    return lqp.LqpProgram(decls, outputs)

def _make_def(ctx: TranslationCtx, name: str, projection: list[lqp.Var], conjs: list[lqp.Formula], exist_vars: list[lqp.Var], is_output: bool = False) -> lqp.Def:
    abstraction = lqp.Abstraction(
        projection,
        mk_exists(
            exist_vars,
            mk_and(conjs)
        ),
    )
    rel_id = name_to_id(name)
    ctx.id_to_orig_name[rel_id] = name

    if is_output:
        ctx.output_ids.append(rel_id)

    # TODO: is this correct? might need attrs tooo?
    return lqp.Def(rel_id, abstraction, [])

# Split the exists into the existential vars, the aggregates, and the other tasks
def _split_exists(ctx: TranslationCtx, task: ir.Exists) -> Tuple[list[ir.Aggregate], list[ir.Task]]:
    if isinstance(task.task, ir.Aggregate):
        return [task.task], []

    if not isinstance(task.task, ir.Logical):
        return [], []

    aggrs = []
    other_tasks = []
    for subtask in task.task.body:
        if isinstance(subtask, ir.Aggregate):
            aggrs.append(subtask)
        else:
            other_tasks.append(subtask)

    return aggrs, other_tasks

def _translate_to_decl(ctx: TranslationCtx, rule: ir.Logical) -> lqp.Declaration:
    effects = []
    body_tasks = []
    aggregates = []

    exist_ir_vars = []

    for task in rule.body:
        if isinstance(task, ir.Output) or isinstance(task, ir.Update):
            effects.append(task)
        elif isinstance(task, ir.Lookup):
            body_tasks.append(task)
        elif isinstance(task, ir.Logical):
            body_tasks.append(task)
        elif isinstance(task, ir.Exists):
            aggrs, others = _split_exists(ctx, task)
            exist_ir_vars.extend(task.vars)
            aggregates.extend(aggrs)
            body_tasks.extend(others)
        elif isinstance(task, ir.Aggregate):
            aggregates.append(task)
        elif isinstance(task, ir.Construct):
            body_tasks.append(task)
        elif isinstance(task, ir.Union):
            body_tasks.append(task)
        else:
            raise NotImplementedError(f"Unknown task type: {type(task)}")

    conjuncts = [_translate_to_formula(ctx, task) for task in body_tasks]

    exist_vars, eqs = translate_bindings(ctx, exist_ir_vars)
    conjuncts.extend(eqs)

    assert len(effects) == 1, f"should only have exactly one effect, got {len(effects)}"
    effect = effects[0]

    if isinstance(effect, ir.Output):
        assert len(aggregates) == 0, "cannot have aggregates in output"
        is_output = True
        def_name = "output"
        projection = []
        for _, v in effect.aliases:
            # TODO: we dont yet handle aliases
            var = _translate_term(ctx, v)
            projection.append(var)

        return _make_def(ctx, def_name, projection, conjuncts, exist_vars, is_output)

    assert isinstance(effect, ir.Update), f"expected update, got {type(effect)}"
    assert_valid_update(effect)
    def_name = effect.relation.name
    is_output = False

    # Handle the bindings
    projection, eqs = translate_bindings(ctx, list(effect.args))
    conjuncts.extend(eqs)

    # Aggregates reduce over the body
    if len(aggregates) > 0:
        aggr_body = mk_and(conjuncts)
        conjuncts = []
        for aggr in aggregates:
            # TODO: what to do with the other result?
            reduce, _ = _translate_aggregate(ctx, aggr, aggr_body, effect)
            conjuncts.append(reduce)
    return _make_def(ctx, def_name, projection, conjuncts, exist_vars, is_output)

def _translate_aggregate(ctx: TranslationCtx, aggr: ir.Aggregate, body: lqp.Formula, update: ir.Update) -> Tuple[lqp.Reduce, list[lqp.Var]]:
    # TODO: handle this properly
    aggr_name = aggr.aggregation.name
    assert aggr_name == "sum" or aggr_name == "count", f"only support sum or count for now, not {aggr.aggregation.name}"

    group_bys = [_translate_term(ctx, var) for var in aggr.group]
    projected_args = [_translate_term(ctx, var) for var in aggr.projection]

    # TODO: differentiate between results and more args
    result_args = []

    # TODO: not sure if this si right
    translated_vars = []
    for arg in aggr.args:
        assert isinstance(arg, ir.Var)
        translated_vars.append(_translate_term(ctx, arg))

    # TODO: input and output should be checked using the aggr not like this
    # Last one is output arg
    output_var = translated_vars[-1]
    result_args.append(output_var)

    # The rest are input args
    input_args = []
    for arg in translated_vars[:-1]:
        input_args.append(arg)

    inner_abstr_args = []
    inner_abstr_args.extend(projected_args)
    inner_abstr_args.extend(input_args)
    if aggr_name == "count":
        # Count sums up "1"
        one_var, eq = binding_to_lqp_var(ctx, 1)
        assert eq is not None
        body = mk_and([body, eq])
        inner_abstr_args.append(one_var)

    outer_abstr_args = []
    for arg in group_bys:
        outer_abstr_args.append(arg)
    outer_abstr_args.append(output_var)

    op = lqp_operator(aggr.aggregation)
    inner_abstr = lqp.Abstraction(
        inner_abstr_args,
        body,
    )
    reduce = lqp.Reduce(
        op,
        inner_abstr,
        result_args,
    )
    return reduce, outer_abstr_args

def _translate_to_formula(ctx: TranslationCtx, task: ir.Task) -> lqp.Formula:
    if isinstance(task, ir.Logical):
        conjuncts = [_translate_to_formula(ctx, child) for child in task.body]
        return mk_and(conjuncts)
    elif isinstance(task, ir.Lookup):
        return _translate_to_atom(ctx, task)
    elif isinstance(task, ir.Exists):
        lqp_vars, conjuncts = translate_bindings(ctx, list(task.vars))
        conjuncts.append(_translate_to_formula(ctx, task.task))
        return mk_exists(lqp_vars, mk_and(conjuncts))
    elif isinstance(task, ir.Construct):
        assert len(task.values) >= 1, "construct should have at least one value"
        # TODO: what does the first value do
        terms = [_translate_term(ctx, arg) for arg in task.values[1:]]
        terms.append(_translate_term(ctx, task.id_var))
        return lqp.Primitive(
            "rel_primitive_hash_tuple_uint128",
            terms,
        )
    elif isinstance(task, ir.Union):
        # TODO: handle hoisted vars if needed
        assert len(task.hoisted) == 0, "hoisted updates not supported yet, because idk what it means"
        disjs = [_translate_to_formula(ctx, child) for child in task.tasks]
        return mk_or(disjs)
    else:
        raise NotImplementedError(f"Unknown task type (formula): {type(task)}")

def _translate_term(ctx: TranslationCtx, value: ir.Value) -> lqp.Term:
    if isinstance(value, ir.Var):
        name = ctx.var_name_cache.get_name(value.id, value.name)
        t = meta_type_to_lqp(value.type)
        return lqp.Var(name, t)
    elif isinstance(value, ir.Literal):
        return lqp.Constant(value.value)
    elif isinstance(value, str):
        return lqp.Constant(value)
    elif isinstance(value, int):
        return lqp.Constant(value)
    else:
        raise NotImplementedError(f"Unknown value type: {type(value)}")

def _translate_to_atom(ctx: TranslationCtx, task: ir.Lookup) -> lqp.Formula:
    # TODO: want signature not name
    rel_name = task.relation.name
    terms = []
    sig_types = []
    for arg in task.args:
        if isinstance(arg, lqp.PrimitiveValue):
            term = lqp.Constant(arg)
            terms.append(term)
            t = type_from_constant(arg)
            sig_types.append(t)
            continue
        assert isinstance(arg, ir.Var), f"expected var, got {type(arg)}: {arg}"
        var = _translate_term(ctx, arg)
        terms.append(var)
        sig_types.append(type_from_term(var))

    # TODO: wrong
    if rel_builtins.is_builtin(task.relation):
        lqp_name = relname_to_lqp_name(task.relation.name)
        return lqp.Primitive(lqp_name, terms)

    rid = get_relation_id(ctx, rel_name, sig_types)
    return lqp.Atom(rid, terms)

def get_relation_id(ctx: TranslationCtx, name: str, types: list[lqp.PrimitiveType]) -> lqp.RelationId:
    relation_id = name_to_id(name)
    ctx.id_to_orig_name[relation_id] = name
    return relation_id

# TODO: should this take types too?
def name_to_id(name: str) -> lqp.RelationId:
    return lqp.RelationId(lqp_hash(name))

def translate_bindings(ctx: TranslationCtx, bindings: list[ir.Value]) -> Tuple[list[lqp.Var], list[lqp.Formula]]:
    lqp_vars = []
    conjuncts = []
    for binding in bindings:
        lqp_var, eq = binding_to_lqp_var(ctx, binding)
        lqp_vars.append(lqp_var)
        if eq is not None:
            conjuncts.append(eq)

    return lqp_vars, conjuncts

def binding_to_lqp_var(ctx: TranslationCtx, binding: ir.Value) -> Tuple[lqp.Var, lqp.Union[None, lqp.Formula]]:
    if isinstance(binding, ir.Var):
        lqp_var = _translate_term(ctx, binding)
        assert isinstance(lqp_var, lqp.Var)
        return lqp_var, None
    else:
        # Constant in this case
        assert isinstance(binding, lqp.PrimitiveValue)
        lqp_value = _translate_term(ctx, binding)

        # TODO: gensym
        var_name = ctx.var_name_cache.get_name(1, "cvar")
        typ = type_from_constant(binding)

        lqp_var = lqp.Var(var_name, typ)
        eq = lqp.Primitive("rel_primitive_eq", [lqp_var, lqp_value])
        return lqp_var, eq
