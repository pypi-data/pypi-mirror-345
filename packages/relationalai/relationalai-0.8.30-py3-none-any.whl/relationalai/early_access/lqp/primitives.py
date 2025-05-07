from relationalai.early_access.lqp import ir as lqp
from relationalai.early_access.metamodel import ir

def relname_to_lqp_name(name: str) -> str:
    # TODO: do these proprly
    if name == "+":
        return "rel_primitive_add"
    elif name == "-":
        return "rel_primitive_subtract"
    elif name == "*":
        return "rel_primitive_multiply"
    elif name == "=":
        return "rel_primitive_eq"
    elif name == "<=":
        return "rel_primitive_lt_eq"
    elif name == ">=":
        return "rel_primitive_gt_eq"
    elif name == "/":
        return "rel_primitive_divide"
    else:
        raise NotImplementedError(f"missing primitive case: {name}")

def lqp_sum_op() -> lqp.Abstraction:
    # TODO: make sure gensym'd properly
    vs = [
        lqp.Var("x", lqp.PrimitiveType.INT),
        lqp.Var("y", lqp.PrimitiveType.INT),
        lqp.Var("z", lqp.PrimitiveType.INT),
    ]

    body = lqp.Primitive("rel_primitive_add", [vs[0], vs[1], vs[2]])
    return lqp.Abstraction(vs, body)

def lqp_operator(op: ir.Relation) -> lqp.Abstraction:
    if op.name == "sum":
        return lqp_sum_op()
    elif op.name == "count":
        return lqp_sum_op()
    else:
        raise NotImplementedError(f"Unsupported aggregation: {op.name}")
