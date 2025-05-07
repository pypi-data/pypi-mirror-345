from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Union, Tuple, Sequence
import datetime as dt

# Tree representation of LQP. Each non-terminal (those with more than one
# option) is an "abstract" class and each terminal is its own class. All of
# which are children of LqpNode. PrimitiveType and PrimitiveValue are
# exceptions. PrimitiveType is an enum and PrimitiveValue is just a value.
# https://docs.google.com/document/d/1QXRU7zc1SUvYkyMCG0KZINZtFgzWsl9-XHxMssdXZzg/

@dataclass(frozen=True)
class LqpNode:
    pass

# Declaration := Def | Loop
@dataclass(frozen=True)
class Declaration(LqpNode):
    pass

# TODO: this should probably be something else
@dataclass(frozen=True)
class LqpProgram:
    defs: list[Declaration]
    # name -> relation id
    outputs: list[Tuple[str, RelationId]]

# Def(name::RelationId, body::Abstraction, attrs::Attribute[])
@dataclass(frozen=True)
class Def(Declaration):
    name: RelationId
    body: Abstraction
    attrs: Sequence[Attribute]

# Loop(temporal_var::LoopIndex, inits::Def[], body::Declaration[])
@dataclass(frozen=True)
class Loop(Declaration):
    temporal_var: str
    inits: Sequence[Def]
    body: Declaration

# Abstraction := Abstraction(vars::Var[], value::Formula)
@dataclass(frozen=True)
class Abstraction(LqpNode):
    vars: Sequence[Var]
    value: Formula

# Formula := Exists
#          | Reduce
#          | Conjunction
#          | Disjunction
#          | Not
#          | FFI
#          | Atom
#          | Pragma
#          | Primitive
#          | True
#          | False
#          | RelAtom
@dataclass(frozen=True)
class Formula(LqpNode):
    pass

# Exists(vars::Var[], value::Formula)
@dataclass(frozen=True)
class Exists(Formula):
    body: Abstraction

# Reduce(op::Abstraction, body::Abstraction, terms::Term[])
@dataclass(frozen=True)
class Reduce(Formula):
    op: Abstraction
    body: Abstraction
    terms: Sequence[Term]

# Conjunction(args::Formula[])
@dataclass(frozen=True)
class Conjunction(Formula):
    args: Sequence[Formula]

# Disjunction(args::Formula[])
@dataclass(frozen=True)
class Disjunction(Formula):
    args: Sequence[Formula]

# Not(arg::Formula)
@dataclass(frozen=True)
class Not(Formula):
    arg: Formula

# FFI(name::Symbol, args::Abstraction[], terms::Term[])
@dataclass(frozen=True)
class Ffi(Formula):
    name: str
    args: Sequence[Abstraction]
    terms: Sequence[Term]

# Atom(name::RelationId, terms::Term[])
@dataclass(frozen=True)
class Atom(Formula):
    name: RelationId
    terms: Sequence[Term]

# Pragma(name::Symbol, terms::Term[])
@dataclass(frozen=True)
class Pragma(Formula):
    name: str
    terms: Sequence[Term]

# Primitive(name::Symbol, terms::Term[])
@dataclass(frozen=True)
class Primitive(Formula):
    name: str
    terms: Sequence[Term]

# True()
@dataclass(frozen=True)
class JustTrue(Formula):
    pass

# False()
@dataclass(frozen=True)
class JustFalse(Formula):
    pass

# RelAtom(name::String, terms::Term[])
@dataclass(frozen=True)
class RelAtom(Formula):
    name: str
    terms: Sequence[Term]

# Term := Var | Constant
@dataclass(frozen=True)
class Term(LqpNode):
    pass

# Var(name::Symbol, type::PrimitiveType)
@dataclass(frozen=True)
class Var(Term):
    name: str
    type: RelType

# Constant(value::PrimitiveValue)
@dataclass(frozen=True)
class Constant(Term):
    value: PrimitiveValue

# Attribute := Attribute(name::Symbol, args::Constant[])
@dataclass(frozen=True)
class Attribute(LqpNode):
    name: str
    args: Sequence[Constant]

# RelationId := RelationId(id::UInt128)
@dataclass(frozen=True)
class RelationId(LqpNode):
    # We use a catchall int here to represent the uint128 as it is difficult
    # to do so in Python without external packages. We check the value in
    # __post_init__.
    id: int

    def __post_init__(self):
        if self.id < 0 or self.id > 0xffffffffffffffffffffffffffffffff:
            raise ValueError(
                "RelationId constructed with out of range (UInt128) number: {}"
                    .format(self.id)
            )

# ValueType
class ValueType(Enum):
    # TODO: fill this out properly
    UNKNOWN = 0
    DECIMAL = 1
    DATE = 2

# PrimitiveType := STRING | DECIMAL | INT | FLOAT | HASH
# TODO: we don't know what types we're supporting yet.
class PrimitiveType(Enum):
    # TODO: get rid of this oen maybe?
    UNKNOWN = 0
    STRING = 1
    INT = 2
    FLOAT = 3
    UINT128 = 4
    DATE = 5

# RelType := PrimitiveType | ValueType
RelType = Union[PrimitiveType, ValueType]

# PrimitiveValue := string | decimal | int | float | hash
# TODO: we don't know what types we're supporting yet.
PrimitiveValue = Union[str, int, float, dt.date]
