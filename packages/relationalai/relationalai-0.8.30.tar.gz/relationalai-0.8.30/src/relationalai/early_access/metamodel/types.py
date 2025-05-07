"""
    Elementary IR types.
"""
from . import ir, util
import sys
from typing import cast
from functools import reduce

#
# Basic Types
#
Null = ir.ScalarType("Null", util.frozen())
Any = ir.ScalarType("Any", util.frozen())
Hash = ir.ScalarType("Hash", util.frozen())
String = ir.ScalarType("String", util.frozen())
Number = ir.ScalarType("Number", util.frozen())
Int = ir.ScalarType("Int", util.ordered_set(Number).frozen())
Float = ir.ScalarType("Float", util.ordered_set(Number).frozen())
Decimal = ir.ScalarType("Decimal", util.ordered_set(Number).frozen())
Bool = ir.ScalarType("Bool", util.frozen())
Binary = ir.ScalarType("Binary", util.ordered_set(Number).frozen()) # 0 or 1
Date = ir.ScalarType("Date", util.frozen())
DateTime = ir.ScalarType("DateTime", util.frozen())
Symbol = ir.ScalarType("Symbol", util.frozen())
Sha1 = ir.ScalarType("SHA1", util.frozen())

AnySet = ir.SetType(Any)
NumberSet = ir.SetType(Number)
StringSet = ir.SetType(String)
IntSet = ir.SetType(Int)

AnyList = ir.ListType(Any)
SymbolList = ir.ListType(Symbol)

def is_builtin(t: ir.Type):
    return t in builtin_types

def _compute_builtin_types() -> list[ir.Type]:
    module = sys.modules[__name__]
    types = []
    for name in dir(module):
        builtin = getattr(module, name)
        if isinstance(builtin, ir.Type):
            types.append(builtin)
    return types

builtin_types = _compute_builtin_types()
builtin_scalar_types_by_name = dict((t.name, t) for t in cast(list[ir.ScalarType], util.filter_by_type(builtin_types, ir.ScalarType)))

def is_any(t: ir.Type) -> bool:
    return t == Any

def is_value_base_type(t: ir.Type) -> bool:
    return isinstance(t, ir.ScalarType) and t in [Hash, String, Number, Int, Float, Decimal, Bool, Binary, Symbol, Sha1]

def is_value_type(t: ir.Type) -> bool:
    if is_value_base_type(t):
        return True
    if isinstance(t, ir.ScalarType):
        t = cast(ir.ScalarType, t)
        if len(t.super_types) == 1:
            # Not sure why we need this cast, but it does shut up the type checker.
            s = cast(ir.Type, t.super_types[0])
            if is_value_type(s):
                return True
    return False

def is_entity_type(t: ir.Type) -> bool:
    return isinstance(t, ir.ScalarType) and not is_value_type(t)

def is_null(t: ir.Type) -> bool:
    return t == Null

def union(*types: ir.Type) -> ir.Type:
    if len(types) == 0:
        return Null
    elif len(types) == 1:
        return types[0]

    if any(isinstance(t, ir.UnionType) for t in types):
        def _union_elements(t: ir.Type) -> util.FrozenOrderedSet[ir.Type]:
            if isinstance(t, ir.UnionType):
                return t.types
            else:
                return util.ordered_set(t).frozen()
        types = tuple([u for t in types for u in _union_elements(t) if not is_null(u)])

    # Remove types subsumed by other types.
    types = tuple([t for t in types if not any(is_proper_subtype(t, s) for s in types)])

    # Check again for the simple cases.
    if len(types) == 0:
        return Null
    elif len(types) == 1:
        return types[0]

    return ir.UnionType(util.ordered_set(*types).frozen())

def intersect(*types: ir.Type) -> ir.Type:
    """
    Intersect a list of types.
    """
    return reduce(intersect_binary, types, Any)

def intersect_binary(t1: ir.Type, t2: ir.Type) -> ir.Type:
    if is_null(t1) or is_null(t2):
        return Null
    elif is_any(t1):
        return t2
    elif is_any(t2):
        return t1
    elif is_subtype(t1, t2):
        return t1
    elif is_subtype(t2, t1):
        return t2
    elif isinstance(t1, ir.UnionType):
        return union(*[intersect_binary(s1, t2) for s1 in t1.types])
    elif isinstance(t2, ir.UnionType):
        return union(*[intersect_binary(t1, s2) for s2 in t2.types])
    elif isinstance(t1, ir.SetType) and isinstance(t2, ir.SetType):
        return ir.SetType(intersect_binary(t1.element_type, t2.element_type))
    elif isinstance(t1, ir.ListType) and isinstance(t2, ir.ListType):
        return ir.ListType(intersect_binary(t1.element_type, t2.element_type))
    elif isinstance(t1, ir.TupleType) and isinstance(t2, ir.TupleType):
        if len(t1.types) != len(t2.types):
            return Null
        else:
            return ir.TupleType(tuple([intersect(s1, s2) for s1, s2 in zip(t1.types, t2.types)]))
    else:
        return Null

def is_proper_subtype(t1: ir.Type, t2: ir.Type) -> bool:
    return t1 != t2 and is_subtype(t1, t2)

def is_subtype(t1: ir.Type, t2: ir.Type) -> bool:
    """
    Check if t1 is a subtype of t2.
    """
    if isinstance(t1, ir.ScalarType) and t2 == Any:
        # Any is the universal supertype of all scalar types.
        return True
    elif t1 == Null and isinstance(t2, ir.ScalarType):
        # Null is the universal subtype of all scalar types.
        return True
    elif isinstance(t1, ir.ScalarType) and isinstance(t2, ir.ScalarType):
        return t1 == t2 or any(is_subtype(s1, t2) for s1 in t1.super_types)
    elif isinstance(t1, ir.SetType) and isinstance(t2, ir.SetType):
        # Sets are covariant.
        return is_subtype(t1.element_type, t2.element_type)
    elif isinstance(t1, ir.ListType) and isinstance(t2, ir.ListType):
        # Lists are covariant.
        return is_subtype(t1.element_type, t2.element_type)
    elif isinstance(t1, ir.TupleType) and isinstance(t2, ir.TupleType):
        # Tuples are covariant.
        return all(is_subtype(a1, a2) for a1, a2 in zip(t1.types, t2.types))
    elif isinstance(t1, ir.TupleType) and isinstance(t2, ir.ListType):
        # list[t] is a supertype of tuple types (t, ...).
        return all(is_subtype(a1, t2.element_type) for a1 in t1.types)
    elif isinstance(t1, ir.UnionType):
        # (t1 | ... | tn) <: t if ti <: t for all i.
        return all(is_subtype(a1, t2) for a1 in t1.types)
    elif isinstance(t2, ir.UnionType):
        # t <: (t1 | ... | tn) if t <: ti for some i.
        return any(is_subtype(t1, a2) for a2 in t2.types)
    else:
        return False
