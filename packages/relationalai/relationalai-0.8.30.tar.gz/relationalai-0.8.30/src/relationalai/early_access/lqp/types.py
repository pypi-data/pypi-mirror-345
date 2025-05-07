from relationalai.early_access.metamodel import ir as meta
from relationalai.early_access.metamodel import types
from relationalai.early_access.lqp import ir as lqp

import datetime as dt

def type_from_term(arg: lqp.Term) -> lqp.RelType:
    if isinstance(arg, lqp.Var):
        return arg.type
    elif isinstance(arg, lqp.Constant):
        return type_from_constant(arg.value)
    else:
        raise NotImplementedError(f"Unknown term type: {type(arg)}")

def meta_type_to_lqp(type: meta.Type) -> lqp.PrimitiveType:
    if isinstance(type, meta.UnionType):
        # TODO - this is WRONG! we need to fix the typer wrt overloading
        type = type.types.some()

    assert isinstance(type, meta.ScalarType)
    if types.is_builtin(type):
        # TODO: just ocompare to types.py
        if type.name == "Int":
            return lqp.PrimitiveType.INT
        elif type.name == "String":
            return lqp.PrimitiveType.STRING
        elif type.name == "Number":
            # TODO: fix this, this is wrong
            return lqp.PrimitiveType.INT
        else:
            # TODO: fix this, this is wrong
            return lqp.PrimitiveType.UNKNOWN
    elif (types.is_entity_type(type)):
        return lqp.PrimitiveType.UINT128
    else:
        raise NotImplementedError(f"Unknown type: {type.name}")

def type_from_constant(arg: lqp.PrimitiveValue) -> lqp.PrimitiveType:
    if isinstance(arg, int):
        return lqp.PrimitiveType.INT
    elif isinstance(arg, float):
        return lqp.PrimitiveType.FLOAT
    elif isinstance(arg, str):
        return lqp.PrimitiveType.STRING
    elif isinstance(arg, dt.date):
        return lqp.PrimitiveType.DATE
    else:
        raise NotImplementedError(f"Unknown constant type: {type(arg)}")
