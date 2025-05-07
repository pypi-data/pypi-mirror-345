from __future__ import annotations
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
import re
from typing import Any, Sequence as PySequence, cast
import itertools

from pandas import DataFrame
import numpy as np
import pandas as pd
from more_itertools import peekable

from relationalai import debugging, errors
from relationalai.early_access.metamodel import factory as f, ir, builtins, types
from relationalai.early_access.metamodel.util import OrderedSet, ordered_set
from relationalai.early_access.rel.executor import RelExecutor
from relationalai.environments import runtime_env

from datetime import date, datetime

#--------------------------------------------------
# Globals
#--------------------------------------------------

_global_id = peekable(itertools.count(0))

# Single context variable with default values
_overrides = ContextVar("overrides", default = {
    "dry_run": False,
    "model_suffix": "",
    "keep_model": True
})
def overrides(key: str):
    return _overrides.get()[key]

@contextmanager
def with_overrides(**kwargs):
    token = _overrides.set({**_overrides.get(), **kwargs})
    try:
        yield
    finally:
        _overrides.reset(token)

#--------------------------------------------------
# Root tracking
#--------------------------------------------------

_track_default = True
_track_roots = ContextVar('track_roots', default=_track_default)
_global_roots = ordered_set()

def _add_root(root):
    if _track_roots.get():
        _global_roots.add(root)

def _remove_roots(items: PySequence[Producer|Fragment]):
    for item in items:
        if hasattr(item, "__hash__") and item.__hash__ and item in _global_roots:
            _global_roots.remove(item)

# decorator
def roots(enabled=_track_default):
    def decorator(func):
        def wrapper(*args, **kwargs):
            token = _track_roots.set(enabled)
            try:
                return func(*args, **kwargs)
            finally:
                _track_roots.reset(token)
        return wrapper
    return decorator

# with root_tracking(enabled=False): ...
@contextmanager
def root_tracking(enabled=_track_default):
    token = _track_roots.set(enabled)
    try:
        yield
    finally:
        _track_roots.reset(token)

#--------------------------------------------------
# Helpers
#--------------------------------------------------

def unwrap_list(item:Any) -> Any:
    if isinstance(item, (list, tuple)) and len(item) == 1:
        return item[0]
    elif isinstance(item, (list, tuple)) and len(item) > 1:
        raise ValueError(f"Expected a single item, got {len(item)}")
    return item

def flatten(items:PySequence[Any]) -> list[Any]:
    flat = []
    for item in items:
        if isinstance(item, (list, tuple)):
            flat.extend(flatten(item))
        else:
            flat.append(item)
    return flat

def find_subjects(items: PySequence[Producer]) -> set[Concept|Ref]:
    subjects = set()
    for item in items:
        if isinstance(item, Concept):
            subjects.add(item)
        elif isinstance(item, ConceptExpression):
            subjects.add(item._op)
        elif isinstance(item, Expression):
            subjects.update(find_subjects(item._params))
        elif isinstance(item, Ref):
            subjects.add(item)
        elif isinstance(item, Relationship) and item._parent:
            subjects.update(find_subjects([item._parent]))
    return subjects

def to_type(item: Any) -> Concept|None:
    if isinstance(item, Concept):
        return item
    elif isinstance(item, (Ref, Alias)):
        return to_type(item._thing)
    elif isinstance(item, ConceptExpression):
        return to_type(item._op)
    elif isinstance(item, Expression):
        return to_type(item._params[-1])

def type_from_type_str(model:Model|None, type_str: str) -> Concept:
    if type_str in Concept.builtins:
        return Concept.builtins[type_str]
    elif model and type_str in model.concepts:
        return model.concepts[type_str]
    else:
        return python_types_to_concepts.get(type(type_str), Concept.builtins["Any"])


def to_name(item:Any) -> str:
    if isinstance(item, Relationship) and isinstance(item._parent, Concept):
        return f"{item._parent._name}_{item._name}"
    elif isinstance(item, (Ref, Alias)):
        return item._name or to_name(item._thing)
    elif isinstance(item, RelationshipRef):
        return item._relationship._name
    elif isinstance(item, ConceptExpression):
        return item._op._name
    return getattr(item, "_name", "v")

def find_model(items: Any) -> Model|None:
    if isinstance(items, (list, tuple)):
        for item in items:
            model = find_model(item)
            if model:
                return model
    elif isinstance(items, dict):
        for item in items.values():
            model = find_model(item)
            if model:
                return model
    else:
        if hasattr(items, "_model") and items._model:
            return items._model
    return None

def find_keys(item: Any, keys:OrderedSet[Any]|None = None) -> OrderedSet[Any]:
    if keys is None:
        keys = ordered_set()
    if isinstance(item, (list, tuple)):
        for it in item:
            find_keys(it, keys)
    elif isinstance(item, Relationship) and item._parent:
        find_keys(item._parent, keys)
    elif isinstance(item, Concept):
        if not item._is_primitive():
            keys.add(item)
    elif isinstance(item, ConceptExpression):
        pass
    elif isinstance(item, Ref):
        if isinstance(item._thing, Concept):
            if not item._thing._is_primitive():
                keys.add(item)
        else:
            find_keys(item._thing, keys)
    elif isinstance(item, RelationshipRef):
        find_keys(item._parent, keys)
    elif isinstance(item, RelationshipFieldRef):
        find_keys(item._relationship, keys)
    elif isinstance(item, Alias):
        find_keys(item._thing, keys)
    elif isinstance(item, Aggregate):
        find_keys(item._group, keys)
    elif isinstance(item, Expression):
        find_keys(item._params, keys)
    elif isinstance(item, Data):
        keys.add(item._row_id)
    elif isinstance(item, DataColumn):
        keys.add(item._data)
    elif isinstance(item, BranchRef):
        find_keys(item._match, keys)
    elif isinstance(item, Match):
        pass
    elif isinstance(item, Distinct):
        pass
    elif isinstance(item, (str, int, float, bool)):
        pass
    else:
        raise ValueError(f"Cannot find keys for {item}")
    return keys

def with_source(item:Any):
    if not hasattr(item, "_source"):
        raise ValueError(f"Item {item} has no source")
    elif item._source is None:
        return {}
    elif debugging.DEBUG:
        source = item._source.to_source_info()
        if source:
            return { "file": source.file, "line": source.line, "source": source.source }
        else:
            return {"file":item._source.file, "line":item._source.line}
    else:
        return {"file":item._source.file, "line":item._source.line}


#--------------------------------------------------
# Producer
#--------------------------------------------------

class Producer:
    def __init__(self, model:Model|None) -> None:
        self._id = next(_global_id)
        self._model = model

    #--------------------------------------------------
    # Infix operator overloads
    #--------------------------------------------------

    def _bin_op(self, op, left, right) -> Expression:
        res = Concept.builtins["Number"].ref("res")
        return Expression(Relationship.builtins[op], left, right, res)

    def __add__(self, other):
        return self._bin_op("+", self, other)
    def __radd__(self, other):
        return self._bin_op("+", other, self)

    def __mul__(self, other):
        return self._bin_op("*", self, other)
    def __rmul__(self, other):
        return self._bin_op("*", other, self)

    def __sub__(self, other):
        return self._bin_op("-", self, other)
    def __rsub__(self, other):
        return self._bin_op("-", other, self)

    def __truediv__(self, other):
        return self._bin_op("/", self, other)
    def __rtruediv__(self, other):
        return self._bin_op("/", other, self)

    def __floordiv__(self, other):
        return self._bin_op("//", self, other)
    def __rfloordiv__(self, other):
        return self._bin_op("//", other, self)

    def __pow__(self, other):
        return self._bin_op("^", self, other)
    def __rpow__(self, other):
        return self._bin_op("^", other, self)

    def __mod__(self, other):
        return self._bin_op("%", self, other)
    def __rmod__(self, other):
        return self._bin_op("%", other, self)

    def __neg__(self):
        return self._bin_op("*", self, -1)

    #--------------------------------------------------
    # Filter overloads
    #--------------------------------------------------

    def _filter(self, op, left, right) -> Expression:
        return Expression(Relationship.builtins[op], left, right)

    def __gt__(self, other):
        return self._filter(">", self, other)
    def __ge__(self, other):
        return self._filter(">=", self, other)
    def __lt__(self, other):
        return self._filter("<", self, other)
    def __le__(self, other):
        return self._filter("<=", self, other)
    def __eq__(self, other) -> Any:
        return self._filter("=", self, other)
    def __ne__(self, other) -> Any:
        return self._filter("!=", self, other)

    #--------------------------------------------------
    # And/Or
    #--------------------------------------------------

    def __or__(self, other) -> Match:
        return Match(self, other)

    def __and__(self, other) -> Fragment:
        if isinstance(other, Fragment):
            return other.where(self)
        return where(self, other)

    #--------------------------------------------------
    # Relationship handling
    #--------------------------------------------------

    def _get_relationship(self, name:str) -> Relationship|RelationshipRef|RelationshipFieldRef:
        root_type = to_type(self) or Concept.builtins["Any"]
        r = Relationship(
            f"{{{root_type}}} has {{{name}:Any}}",
            parent=self, short_name=name, model=self._model
        )
        return r

    #--------------------------------------------------
    # getattr
    #--------------------------------------------------

    def __getattr__(self, name:str) -> Any:
        if name.startswith("_"):
            raise AttributeError(f"{type(self).__name__} has no attribute {name}")
        if not hasattr(self, "_relationships"):
            return super().__getattribute__(name)
        if name not in self._relationships:
            self._relationships[name] = self._get_relationship(name)
        return self._relationships[name]

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            super().__setattr__(name, value)
        elif isinstance(value, Relationship):
            value._parent = self
            value._short_name = name
            self._relationships[name] = value
        else:
            raise AttributeError(f"Cannot set attribute {name} on {type(self).__name__}")

    #--------------------------------------------------
    # ref + alias
    #--------------------------------------------------

    def ref(self, name:str|None=None) -> Ref|RelationshipRef:
        return Ref(self, name=name)

    def alias(self, name:str) -> Alias:
        return Alias(self, name)

    #--------------------------------------------------
    # Find model
    #--------------------------------------------------

    def _find_model(self, items:list[Any]) -> Model|None:
        if self._model:
            return self._model

        for item in items:
            if isinstance(item, (Producer, Fragment)) and item._model:
                self._model = item._model
                return item._model
        return None

    #--------------------------------------------------
    # Hash
    #--------------------------------------------------

    __hash__ = object.__hash__

    #--------------------------------------------------
    # _pprint
    #--------------------------------------------------

    def _pprint(self, indent:int=0) -> str:
        return str(self)

    #--------------------------------------------------
    # Fallbacks
    #--------------------------------------------------

    def select(self, *args: Any):
        raise NotImplementedError(f"`{type(self).__name__}.select` not implemented")

    def where(self, *args: Any):
        raise NotImplementedError(f"`{type(self).__name__}.where` not implemented")

    def require(self, *args: Any):
        raise NotImplementedError(f"`{type(self).__name__}.require` not implemented")

    def define(self, *args: Any):
        raise NotImplementedError(f"`{type(self).__name__}.then` not implemented")

#--------------------------------------------------
# Ref
#--------------------------------------------------

class Ref(Producer):
    def __init__(self, thing:Producer, name:str|None=None):
        super().__init__(thing._model)
        self._thing = thing
        self._name = name
        self._no_lookup = False
        self._relationships = {}

    def _get_relationship(self, name: str) -> Relationship | RelationshipRef:
        rel = getattr(self._thing, name)
        return RelationshipRef(self, rel)

    def __str__(self) -> str:
        if self._name:
            return f"{self._name}{self._id}"
        return f"{self._thing}{self._id}"

class RelationshipRef(Producer):
    def __init__(self, parent:Any, relationship:Relationship|RelationshipRef, name:str|None=None):
        super().__init__(find_model([parent, relationship]))
        self._parent = parent
        if isinstance(relationship, RelationshipRef):
            relationship = relationship._relationship
        self._relationship:Relationship = relationship
        self._field_refs = [r.ref() for r in relationship._field_refs]
        if name:
            self._field_refs[-1].name = name
        self._relationships = {}

    def _get_relationship(self, name: str) -> Relationship|RelationshipRef|RelationshipFieldRef:
        rel = super()._get_relationship(name)
        if isinstance(rel, Relationship):
            return RelationshipRef(self, rel)
        elif isinstance(rel, RelationshipFieldRef):
            return RelationshipFieldRef(self, rel._relationship, rel._field_ix)
        else:
            return rel

    def __call__(self, *args: Any) -> Any:
        clean_args = list(args)
        if len(args) < len(self._relationship._fields):
            clean_args = [self._parent, *clean_args]
        return Expression(self._relationship, *clean_args)

    def __str__(self) -> str:
        return f"{self._parent}.{self._relationship._short_name}"

class RelationshipFieldRef(Producer):
    def __init__(self, parent:Any, relationship:Relationship|RelationshipRef, field_ix:int):
        super().__init__(find_model([relationship]))
        self._parent = parent
        if isinstance(relationship, RelationshipRef):
            relationship = relationship._relationship
        self._relationship:Relationship = relationship
        self._field_ix = field_ix
        self._relationships = {}

    @property
    def _field_ref(self) -> Ref|RelationshipRef:
        return self._relationship._field_refs[self._field_ix]

    def _get_relationship(self, name: str) -> Relationship | RelationshipRef:
        rel = getattr(self._field_ref, name)
        return RelationshipRef(self, rel)

    def __call__(self, arg: Any) -> Any:
        return self == arg

    def __str__(self) -> str:
        return f"{self._relationship}.{self._field_ref}"

#--------------------------------------------------
# Concept
#--------------------------------------------------

class Concept(Producer):
    builtins = {}

    def __init__(self, name:str, extends:list[Any] = [], model:Model|None=None):
        super().__init__(model)
        self._name = name
        self._relationships = {}
        self._extends = []
        for e in extends:
            if isinstance(e, Concept):
                self._extends.append(e)
            elif python_types_to_concepts.get(e):
                self._extends.append(python_types_to_concepts[e])
            else:
                raise ValueError(f"Unknown concept {e} in extends")
        self._annotations = []

    def require(self, *args: Any) -> Fragment:
        return where(self).require(*args)

    def new(self, ident: Any|None=None, **kwargs) -> ConceptNew:
        return ConceptNew(self, ident, kwargs)

    def new_identity(self, args: Any|None=None, **kwargs: Any) -> ConceptConstruct:
        return ConceptConstruct(self, args, kwargs)

    def annotate(self, *annos:Expression|Relationship) -> Concept:
        self._annotations.extend(annos)
        return self

    def _get_relationship(self, name: str) -> Relationship | RelationshipRef | RelationshipFieldRef:
        for parent in self._extends:
            if name in parent._relationships:
                return RelationshipRef(self, parent._relationships[name])
        return super()._get_relationship(name)

    def _isa(self, other:Concept) -> bool:
        if self is other:
            return True
        for parent in self._extends:
            if parent._isa(other):
                return True
        return False

    def _is_primitive(self) -> bool:
        return self._isa(Primitive)

    def _is_filter(self) -> bool:
        return False

    def __call__(self, identity:Any=None, **kwargs: Any) -> ConceptMember:
        return ConceptMember(self, identity, kwargs)

    def __str__(self):
        return self._name

#--------------------------------------------------
# ErrorConcept
#--------------------------------------------------

class ErrorConcept(Concept):
    _error_props = OrderedSet()
    _relation = None

    def __init__(self, name:str, extends:list[Any] = [], model:Model|None=None):
        super().__init__(name, extends, model)

    def new(self, ident: Any|None=None, **kwargs) -> ConceptNew:
        model = kwargs.get("_model") or find_model([ident, kwargs])
        if kwargs.get("_model"):
            del kwargs["_model"]

        if not ErrorConcept._relation:
            ErrorConcept._relation = Relationship(
                "{Error} has {attribute:Any} with {value:Any}",
                short_name="pyrel_error_attrs",
                model=model
            )
        source = None
        if "_source" in kwargs:
            source = kwargs["_source"]
            del kwargs["_source"]
        else:
            source = runtime_env.get_source_pos()
        # kwargs["severity"] = "error"
        if source:
            source = source.to_source_info()
            source_id = len(errors.ModelError.error_locations)
            errors.ModelError.error_locations[source_id] = source
            kwargs["pyrel_id"] = source_id

        for k, v in kwargs.items():
            if (model, k) not in ErrorConcept._error_props and not k.startswith("_"):
                ErrorConcept._error_props.add((model, k))
                with root_tracking(True):
                    frag = where(getattr(self, k)).define(
                        ErrorConcept._relation(self, k, getattr(self, k))
                    )
                    frag._model = model
        return super().new(ident, **kwargs)

    def __call__(self, identity: Any = None, **kwargs: Any) -> Any:
        raise ValueError("Errors must always be created with a new identity. Use Error.new(..) instead of Error(..)")

#--------------------------------------------------
# Builtin Concepts
#--------------------------------------------------

Primitive = Concept.builtins["Primitive"] = Concept("Primitive")
Error = Concept.builtins["Error"] = ErrorConcept("Error")

# Load builtin types
for builtin in types.builtin_types:
    if isinstance(builtin, ir.ScalarType):
        Concept.builtins[builtin.name] = Concept(builtin.name, extends=[Primitive])

Float = Concept.builtins["Float"]
Integer = Concept.builtins["Int"]
Decimal = Concept.builtins["Decimal"]
String = Concept.builtins["String"]
Bool = Concept.builtins["Bool"]
Date = Concept.builtins["Date"]
DateTime = Concept.builtins["DateTime"]

# The following is a workaround for having the builtin "Int"
# but not other the builtin "Integer". The `Relationship`
# class relies upon the builtin "Integer" existing in its
# _build_inspection_fragment() method.
Concept.builtins["Integer"] = Concept.builtins["Int"]

python_types_to_concepts = {
    int: Concept.builtins["Int"],
    float: Concept.builtins["Float"],
    str: Concept.builtins["String"],
    bool: Concept.builtins["Bool"],
    date: Concept.builtins["Date"],
    datetime: Concept.builtins["DateTime"],

    # Pandas/NumPy dtype objects
    np.dtype('int64'): Concept.builtins["Int"],
    np.dtype('int32'): Concept.builtins["Int"],
    np.dtype('int16'): Concept.builtins["Int"],
    np.dtype('int8'): Concept.builtins["Int"],
    np.dtype('uint64'): Concept.builtins["Int"],
    np.dtype('uint32'): Concept.builtins["Int"],
    np.dtype('uint16'): Concept.builtins["Int"],
    np.dtype('uint8'): Concept.builtins["Int"],
    np.dtype('float64'): Concept.builtins["Float"],
    np.dtype('float32'): Concept.builtins["Float"],
    np.dtype('bool'): Concept.builtins["Bool"],
    np.dtype('object'): Concept.builtins["String"],  # Often strings are stored as object dtype

    # Pandas extension dtypes
    pd.Int64Dtype(): Concept.builtins["Int"],
    pd.Int32Dtype(): Concept.builtins["Int"],
    pd.Int16Dtype(): Concept.builtins["Int"],
    pd.Int8Dtype(): Concept.builtins["Int"],
    pd.UInt64Dtype(): Concept.builtins["Int"],
    pd.UInt32Dtype(): Concept.builtins["Int"],
    pd.UInt16Dtype(): Concept.builtins["Int"],
    pd.UInt8Dtype(): Concept.builtins["Int"],
    pd.Float64Dtype(): Concept.builtins["Float"],
    pd.Float32Dtype(): Concept.builtins["Float"],
    pd.StringDtype(): Concept.builtins["String"],
    pd.BooleanDtype(): Concept.builtins["Bool"],

}

#--------------------------------------------------
# Relationship
#--------------------------------------------------

@dataclass
class Field():
    name:str
    type_str:str
    is_many:bool = False

class Relationship(Producer):
    builtins = {}

    def __init__(self, madlib:Any, parent:Producer|None=None, short_name:str="", model:Model|None=None, fields:list[Field]|None=None, ir_relation:ir.Relation|None=None):
        found_model = model or find_model(parent) or find_model(args)
        super().__init__(found_model)
        self._parent = parent
        self._madlib = madlib
        self._short_name = short_name or self._default_short_name(madlib)
        self._relationships = {}
        self._fields:list[Field] = fields or self._parse_schema_format(madlib)
        if not self._fields and not ir_relation:
            raise ValueError(f"No fields found in relationship {self}")
        self._ir_relation = ir_relation

        self._field_refs = [cast(Ref, type_from_type_str(found_model, field.type_str).ref(field.name)) for field in self._fields]
        for field in self._field_refs:
            field._no_lookup = True
        self._field_names = [field.name for field in self._fields]
        self._annotations = []

    @property
    def _name(self):
        return self._short_name or self._madlib

    def _is_filter(self) -> bool:
        return self._short_name in [">", "<", "=", "!=", ">=", "<="]

    def _default_short_name(self, madlib:Any) -> str:
        # Replace curly braces, colons, and spaces with underscores.
        # Then strip leading/trailing underscores.
        return re.sub(r"[{}: ]", "_", str(madlib)).strip("_")

    def _parse_schema_format(self, format_string:str):
        # Pattern to extract fields like {Type*} or {name:Type*}
        pattern = r'\{([a-zA-Z0-9_]+)(\*?)(?::([a-zA-Z0-9_]+)(\*?))?\}'
        matches = re.findall(pattern, format_string)

        used_names = set()
        fields = []
        for field_name, field_name_is_many, field_type, field_type_is_many in matches:
            # If no type is specified, use the field name as the type
            if not field_type:
                field_type = field_name
                field_name = field_name.lower()
                field_type_is_many = field_name_is_many

            ix = 2
            while field_name in used_names:
                field_name = f"{field_name}{ix}"
                ix += 1
            used_names.add(field_name)

            fields.append(Field(field_name, field_type, bool(field_type_is_many)))

        return fields

    def _get_relationship(self, name: str) -> Relationship | RelationshipRef | RelationshipFieldRef:
        rel = getattr(self._field_refs[-1], name)
        return RelationshipRef(self, rel._relationship)

    def __getattr__(self, name: str) -> Any:
        if len(self._fields) > 2 and name in self._field_names:
            return RelationshipFieldRef(self._parent, self, self._field_names.index(name))
        return super().__getattr__(name)

    def annotate(self, *annos:Expression|Relationship) -> Relationship:
        self._annotations.extend(annos)
        return self

    def ref(self, name:str|None=None) -> Ref|RelationshipRef:
        return RelationshipRef(self._parent, self, name=name)

    def _build_inspection_fragment(self):
        """
        Helper function for the inspect() and to_df() methods below,
        that generates a Fragment from the Relationship, inspect()ing
        or to_df()'ing which yields all tuples in the Relationship.
        """
        field_types = [type_from_type_str(self._model, field.type_str) for field in self._fields]
        field_vars = [field_type.ref() for field_type in field_types]
        return where(self(*field_vars)).select(*field_vars)

    def inspect(self):
        return self._build_inspection_fragment().inspect()

    def to_df(self):
        return self._build_inspection_fragment().to_df()

    def __call__(self, *args: Any, **kwargs) -> Any:
        if kwargs and args:
            raise ValueError("Cannot use both positional and keyword arguments")
        if kwargs:
            # check that all fields have been provided
            clean_args = []
            for ix, field in enumerate(self._field_names):
                if field in kwargs:
                    clean_args.append(kwargs.get(field))
                if ix == 0 and self._parent:
                    continue
                if field not in kwargs:
                    raise ValueError(f"Missing argument {field}")
        else:
            clean_args = list(args)
        if len(clean_args) < len(self._fields):
            if self._parent:
                clean_args = [self._parent, *clean_args]
        if len(clean_args) != len(self._fields):
            raise ValueError(f"Expected {len(self._fields)} arguments, got {len(clean_args)}")
        return Expression(self, *clean_args)

    def __str__(self):
        if self._parent and self._short_name:
            return f"{self._parent}.{self._short_name}"
        return self._name

#--------------------------------------------------
# Builtin Relationships
#--------------------------------------------------

for builtin in builtins.builtin_relations + builtins.builtin_annotations:
    fields = []
    for field in builtin.fields:
        field_type = re.sub(r'[\]\}]', '*', re.sub(r'[\[\{\(]', '', str(field.type))).strip()
        fields.append(f"{field.name}:{field_type}")
    args = ' '.join([f"{{{f}}}"for f in fields])
    Relationship.builtins[builtin.name] =  Relationship(f"{builtin.name} {args}", parent=None, short_name=builtin.name, ir_relation=builtin)

RawSource = Relationship.builtins["raw_source"]


#--------------------------------------------------
# Expression
#--------------------------------------------------

infix_ops = ["+", "-", "*", "/", "//", "^", "%", ">", ">=", "<", "<=", "=", "!="]

class Expression(Producer):
    def __init__(self, op:Relationship|Concept, *params:Any):
        super().__init__(op._model or find_model(params))
        self._op = op
        self._params = params
        self._source = runtime_env.get_source_pos()

    def __str__(self):
        return f"({self._op} {' '.join(map(str, self._params))})"

    def _pprint(self, indent:int=0) -> str:
        if self._op._name in infix_ops:
            a, b = self._params[0], self._params[1]
            return f"{' ' * indent}{a} {self._op} {b}"
        return f"{' ' * indent}{self._op}({' '.join(map(str, self._params))})"

    def __getattr__(self, name: str):
        raise AttributeError(f"Expression has no attribute {name}")

class ConceptExpression(Expression):
    def __init__(self, con:Concept, identity:Any, kwargs:dict[str, Any]):
        super().__init__(con, identity, kwargs)
        for k, v in kwargs.items():
            # make sure to create the properties being referenced
            getattr(self._op, k)
        self._relationships = {}

    def _get_relationship(self, name: str) -> Relationship|RelationshipRef:
        parent_rel = getattr(self._op, name)
        return RelationshipRef(self, parent_rel)

    def __getattr__(self, name: str):
        return Producer.__getattr__(self, name)

class ConceptMember(ConceptExpression):
    def __init__(self, con:Concept, identity:Any, kwargs:dict[str, Any]):
        super().__init__(con, identity, kwargs)
        if not identity:
            class_name = con._name
            raise ValueError(f"Adding or looking up an instance of Concept requires an identity. If you want to create a new identity, use {class_name}.new(..)")
        # TODO: when we do reference schemes, the identity might be
        # in a combination of kwargs rather than in the positionals


class ConceptNew(ConceptExpression):
    def __str__(self):
        return f"({self._op}.new {' '.join(map(str, self._params))})"


class ConceptConstruct(ConceptExpression):
    pass

#--------------------------------------------------
# Aggregate
#--------------------------------------------------

class Aggregate(Producer):
    def __init__(self, op:Relationship, *args: Any):
        super().__init__(op._model or find_model(args))
        self._op = op
        self._args = args
        _remove_roots(args)
        self._group = []
        self._where = where()

    def where(self, *args: Any) -> Aggregate:
        new = self.clone()
        if not new._model:
            new._model = find_model(args)
        new._where = new._where.where(*args)
        return new

    def per(self, *args: Any) -> Aggregate:
        new = self.clone()
        if not new._model:
            new._model = find_model(args)
        new._group.extend(args)
        return new

    def clone(self) -> Aggregate:
        clone = Aggregate(self._op, *self._args)
        clone._group = self._group.copy()
        clone._where = self._where
        return clone

    def __getattr__(self, name: str):
        raise AttributeError(f"Expression has no attribute {name}")

    def __str__(self):
        args = ', '.join(map(str, self._args))
        group = ', '.join(map(str, self._group))
        where = ""
        if group:
            group = f" (per {group})"
        if self._where._where:
            items = ', '.join(map(str, self._where._where))
            where = f" (where {items})"
        return f"({self._op} {args}{group}{where})"

class Group():
    def __init__(self, *args: Any):
        self._group = args

    def __str__(self):
        args = ', '.join(map(str, self._group))
        return f"(per {args})"

    #--------------------------------------------------
    # Agg funcs
    #--------------------------------------------------

    def count(self, *args: Any) -> Aggregate:
        return Aggregate(Relationship.builtins["count"], *args).per(*self._group)

    def sum(self, *args: Any) -> Aggregate:
        return Aggregate(Relationship.builtins["sum"], *args).per(*self._group)

    def avg(self, *args: Any) -> Aggregate:
        return Aggregate(Relationship.builtins["avg"], *args).per(*self._group)

    def min(self, *args: Any) -> Aggregate:
        return Aggregate(Relationship.builtins["min"], *args).per(*self._group)

    def max(self, *args: Any) -> Aggregate:
        return Aggregate(Relationship.builtins["max"], *args).per(*self._group)

#--------------------------------------------------
# Aggregate builtins
#--------------------------------------------------

def per(*args: Any) -> Group:
    return Group(*args)

def count(*args: Any) -> Aggregate:
    return Aggregate(Relationship.builtins["count"], *args)

def sum(*args: Any) -> Aggregate:
    return Aggregate(Relationship.builtins["sum"], *args)

def avg(*args: Any) -> Aggregate:
    return Aggregate(Relationship.builtins["avg"], *args)

def min(*args: Any) -> Aggregate:
    return Aggregate(Relationship.builtins["min"], *args)

def max(*args: Any) -> Aggregate:
    return Aggregate(Relationship.builtins["max"], *args)

#--------------------------------------------------
# Alias
#--------------------------------------------------

class Alias(Producer):
    def __init__(self, thing:Producer, name:str):
        super().__init__(thing._model)
        self._thing = thing
        self._name = name
        self._relationships = {}
        _remove_roots([thing])

    def __str__(self) -> str:
        return f"{self._thing} as {self._name}"

#--------------------------------------------------
# Match
#--------------------------------------------------

class BranchRef(Producer):
    def __init__(self, match:Match, ix:int):
        super().__init__(match._model)
        self._match = match
        self._ix = ix

    def __str__(self):
        return f"{self._match}#{self._ix}"

class Match(Producer):
    def __init__(self, *args: Any):
        super().__init__(find_model(args))
        self._args = list(self._flatten_args(args))
        if any(isinstance(arg, Fragment) and arg._is_effect() for arg in self._args):
            _add_root(self)
        _remove_roots(args)

        # check for validity
        is_select = None
        ret_count = 0
        for arg in self._args:
            if isinstance(arg, Fragment) and arg._is_effect():
                if is_select:
                    raise ValueError("Cannot mix expression and effect clauses in a match")
                is_select = False
            elif isinstance(arg, Fragment) and not arg._is_effect():
                if is_select is False:
                    raise ValueError("Cannot mix effect and expression clauses in a match")
                is_select = True
                if ret_count == 0:
                    ret_count = len(arg._select)
                elif ret_count != len(arg._select):
                    raise ValueError("All clauses must have the same number of return values")
            elif isinstance(arg, (str, int, float, bool)):
                if is_select is False:
                    raise ValueError("Cannot mix then and select clauses in a match")
                is_select = True
                if ret_count == 0:
                    ret_count = 1
                elif ret_count != 1:
                    raise ValueError("All clauses must have the same number of return values")
            elif isinstance(arg, Expression) or isinstance(arg, Aggregate):
                if is_select is None:
                    is_select = True
                    if not arg._op._is_filter():
                        ret_count = 1
            elif isinstance(arg, Relationship) or isinstance(arg, Ref):
                if is_select is None:
                    is_select = True
                    ret_count = 1

        self._is_select = is_select
        self._ret_count = ret_count
        self._source = runtime_env.get_source_pos()

    def _flatten_args(self, args):
        for arg in args:
            if isinstance(arg, Match):
                for sub_arg in arg._args:
                    yield sub_arg
            else:
                yield arg

    def __iter__(self):
        for ix in range(self._ret_count):
            yield BranchRef(self, ix)

    def __str__(self):
        return " | ".join(map(str, self._args))

#---------------------------------------------/-----
# Union
#--------------------------------------------------

class Union(Match):
    def __str__(self):
        return " & ".join(map(str, self._args))

def union(*args: Any) -> Union:
    return Union(*args)

#--------------------------------------------------
# Quantifiers
#--------------------------------------------------

class Quantifier():
    def __init__(self, *args: Any):
        self._args = args
        self._model = find_model(args)
        _remove_roots(args)
        self._where = where()

    def where(self, *args: Any) -> Quantifier:
        new = self.clone()
        if not new._model:
            new._model = find_model(args)
        new._where = new._where.where(*args)
        return new

    def clone(self) -> Quantifier:
        clone = type(self)(*self._args)
        clone._where = self._where
        return clone

class Exists(Quantifier):
    def __str__(self):
        args_str = ','.join(map(str, self._args))
        where_items = '\n        '.join(map(str, self._where._where))
        where = f"\n        {where_items}" if self._where._where else ""
        return f"(exists [{args_str}]{where})"

class Forall(Quantifier):
    def __str__(self):
        args_str = ','.join(map(str, self._args))
        where_items = '\n        '.join(map(str, self._where._where))
        where = f"\n        {where_items}" if self._where._where else ""
        return f"(forall [{args_str}]{where})"

class Not(Quantifier):
    def where(self, *args: Any) -> Quantifier:
        raise NotImplementedError("Not cannot have a where clause")

    def __str__(self):
        args_str = '\n    '.join(map(str, self._args))
        return f"(not {args_str})"

def exists(*args: Any) -> Exists:
    return Exists(*args)

def forall(*args: Any) -> Forall:
    return Forall(*args)

def not_(*args: Any) -> Not:
    return Not(*args)

#--------------------------------------------------
# Distinct
#--------------------------------------------------

class Distinct():
    def __init__(self, *args: Any):
        self._args = args
        self._model = find_model(args)
        _remove_roots(args)

def distinct(*args: Any) -> Distinct:
    return Distinct(*args)

#--------------------------------------------------
# Data
#--------------------------------------------------

class DataColumn(Producer):
    def __init__(self, data:Data, _type, name:str):
        self._data = data
        self._type = _type
        self._name = name if isinstance(name, str) else f"v{name}"
        self._ref = python_types_to_concepts[_type].ref(self._name)

    def __str__(self):
        return f"DataColumn({self._name}, {self._type})"

class Data(Producer):
    def __init__(self, data:DataFrame):
        super().__init__(None)
        self._data = data
        self._relationships = {}
        self._cols = []
        self._row_id = Integer.ref("row_id")
        for col in data.columns:
            t = data[col].dtype
            self._cols.append(DataColumn(self, t, col))
            self._relationships[col] = self._cols[-1]

    def into(self, concept:Concept, keys:list[str]=[]):
        if keys:
            new = concept.new_identity(**{k.lower(): getattr(self, k) for k in keys})
        else:
            new = concept.new_identity(self._row_id)
        where(self, new).define(
            concept(new),
            *[getattr(concept, col._name)(new, col) for col in self._cols]
        )

    def __getitem__(self, item: str|int) -> DataColumn:
        if isinstance(item, int):
            return self._cols[item]
        if item in self._relationships:
            return self._relationships[item]
        raise KeyError(f"Data has no column {item}")

    def _get_relationship(self, name: str) -> Relationship | RelationshipRef | RelationshipFieldRef:
        raise AttributeError(f"Data has no attribute {name}")

    def __str__(self):
        return f"Data({len(self._data)} rows, [{', '.join([str(c) for c in self._cols])}])"

    def __hash__(self):
        return hash(self._id)

def _to_df(data: DataFrame | list[tuple] | list[dict], columns:list[str]|None) -> DataFrame:
    if isinstance(data, DataFrame):
        return data
    if not data:
        return DataFrame()
    if isinstance(data, list):
        if isinstance(data[0], tuple):
            # Named tuple check
            if hasattr(data[0], '_fields'):
                return DataFrame([t._asdict() for t in data]) #type: ignore
            return DataFrame(data, columns=columns)
        elif isinstance(data[0], dict):
            return DataFrame(data)
    raise TypeError(f"Cannot convert {type(data)} to DataFrame. Use DataFrame, list of tuples, or list of dicts.")

def data(data:DataFrame|list[tuple]|list[dict], columns:list[str]|None=None) -> Data:
    return Data(_to_df(data, columns))

#--------------------------------------------------
# Fragment
#--------------------------------------------------

class Fragment():
    def __init__(self, parent:Fragment|None=None, model:Model|None=None):
        self._id = next(_global_id)
        self._select = []
        self._where = []
        self._require = []
        self._define = []
        self._model = parent._model if parent else model
        self._parent = parent
        self._source = runtime_env.get_source_pos()
        self._meta = {}
        self._annotations = []
        if parent:
            self._select.extend(parent._select)
            self._where.extend(parent._where)
            self._require.extend(parent._require)
            self._define.extend(parent._define)

    def _add_items(self, items:PySequence[Any], to_attr:list[Any]):
        # TODO: ensure that you are _either_ a select, require, or then
        # not a mix of them
        _remove_roots(items)
        to_attr.extend(items)

        if self._define or self._require:
            if self._parent:
                _remove_roots([self._parent])
            _add_root(self)

        if not self._model:
            self._model = find_model(items)
        return self

    def where(self, *args: Any) -> Fragment:
        f = Fragment(parent=self)
        return f._add_items(args, f._where)

    def select(self, *args: Any) -> Fragment:
        f = Fragment(parent=self)
        return f._add_items(args, f._select)

    def require(self, *args: Any) -> Fragment:
        f = Fragment(parent=self)
        return f._add_items(args, f._require)

    def define(self, *args: Any) -> Fragment:
        f = Fragment(parent=self)
        return f._add_items(args, f._define)

    def meta(self, **kwargs: Any) -> Fragment:
        self._meta.update(kwargs)
        return self

    def annotate(self, *annos:Expression|Relationship) -> Fragment:
        self._annotations.extend(annos)
        return self

    #--------------------------------------------------
    # helpers
    #--------------------------------------------------

    def _is_effect(self) -> bool:
        return bool(self._define or self._require or (self._parent and self._parent._is_effect()))

    def _is_where_only(self) -> bool:
        return not self._select and not self._define and not self._require

    #--------------------------------------------------
    # And/Or
    #--------------------------------------------------

    def __or__(self, other) -> Match:
        return Match(self, other)

    def __and__(self, other) -> Union:
        return Union(self, other)

    #--------------------------------------------------
    # Stringify
    #--------------------------------------------------

    def __str__(self):
        sections = []
        if self._select:
            select = '\n    '.join(map(str, self._select))
            sections.append(f"(select\n    {select})")
        if self._where:
            where = '\n    '.join(map(str, self._where))
            sections.append(f"(where\n    {where})")
        if self._require:
            require = '\n    '.join(map(str, self._require))
            sections.append(f"(require\n    {require})")
        if self._define:
            effects = '\n    '.join(map(str, self._define))
            sections.append(f"(then\n    {effects})")

        return "\n".join(sections)

    #--------------------------------------------------
    # Execute
    #--------------------------------------------------

    def __iter__(self):
        # Iterate over the rows of the fragment's results
        return self.to_df().itertuples(index=False).__iter__()

    def inspect(self):
        # @TODO what format? maybe ignore row indices?
        print(self.to_df())

    def to_df(self):
        """Convert the fragment's results to a pandas DataFrame."""
        # @TODO currently this code assumes a Rel executor; should dispatch based on config

        qb_model = self._model or Model("anon")
        ir_model = qb_model._to_ir()
        self._source = runtime_env.get_source_pos()
        with debugging.span("query", dsl=str(self), **with_source(self), meta=self._meta) as query_span:
            query_task = qb_model._compiler.fragment(self)
            results = qb_model._to_executor().execute(ir_model, query_task)
            query_span["results"] = results
            return results

#--------------------------------------------------
# Select / Where
#--------------------------------------------------

def select(*args: Any, parent:Fragment|None=None, model:Model|None=None) -> Fragment:
    return Fragment(model=model).select(*args)

def where(*args: Any, parent:Fragment|None=None, model:Model|None=None) -> Fragment:
    return Fragment(model=model).where(*args)

def require(*args: Any, parent:Fragment|None=None, model:Model|None=None) -> Fragment:
    return Fragment(model=model).require(*args)

def define(*args: Any, parent:Fragment|None=None, model:Model|None=None) -> Fragment:
    return Fragment(model=model).define(*args)

#--------------------------------------------------
# Model
#--------------------------------------------------

class Model():
    def __init__(self, name:str, dry_run: bool = False, keep_model: bool = True):
        self._id = next(_global_id)
        self.name = f"{name}{overrides('model_suffix')}"
        self._dry_run = cast(bool, dry_run or overrides('dry_run'))
        self._keep_model = cast(bool, keep_model and overrides('keep_model'))
        self.concepts:dict[str, Concept] = {}
        self.relationships:list[Relationship] = []

        # Compiler
        self._compiler = Compiler()
        self._root_version = _global_roots.version()
        self._last_compilation = None

        # Executor
        self._executor = None

    def _to_ir(self):
        if not _global_roots.has_changed(self._root_version) and self._last_compilation:
            return self._last_compilation
        self._last_compilation = self._compiler.model(self)
        self._root_version = _global_roots.version()
        return self._last_compilation

    def _to_executor(self):
        if not self._executor:
            self._executor = RelExecutor(self.name, dry_run=self._dry_run, keep_model=self._keep_model)
        return self._executor

    def Concept(self, name:str, extends:list[Concept|Any]=[]) -> Concept:
        if name not in self.concepts:
            self.concepts[name] = Concept(name, model=self, extends=extends)
        return self.concepts[name]

    def Relationship(self, *args) -> Relationship:
        return Relationship(*args, parent=None, short_name="", model=self)

    def define(self, *args: Any) -> Fragment:
        return define(*args, model=self)

#--------------------------------------------------
# Compile
#--------------------------------------------------

class CompilerContext():
    def __init__(self, compiler:Compiler, parent:CompilerContext|None=None):
        self.compiler = compiler
        self.parent = parent
        self.value_map:dict[Producer, ir.Value|list[ir.Var]] = parent.value_map.copy() if parent else {}
        self.items:OrderedSet[ir.Task] = OrderedSet()
        self.into_vars:list[ir.Var] = parent.into_vars.copy() if parent else []
        self.global_value_map:dict[Producer, ir.Value|list[ir.Var]] = parent.global_value_map if parent else {}

    def to_value(self, item:Producer) -> ir.Value|list[ir.Var]:
        if item not in self.value_map:
            if item in self.global_value_map:
                self.value_map[item] = self.global_value_map[item]
            else:
                name = to_name(item)
                qb_type = to_type(item)
                type = self.compiler.to_type(qb_type) if qb_type else types.Any
                name = name.lower()
                self.map_var(item, f.var(name, type))
        return self.value_map[item]

    def map_var(self, item:Producer, value:ir.Value|list[ir.Var]):
        self.global_value_map[item] = value
        self.value_map[item] = value

    def _has_item(self, item:ir.Task) -> bool:
        return bool(item in self.items or (self.parent and self.parent._has_item(item)))

    def add(self, item:ir.Task):
        if not self._has_item(item):
            self.items.add(item)

    def try_merge_hoists(self, required: PySequence[ir.VarOrDefault], available: PySequence[ir.VarOrDefault]) -> list[ir.VarOrDefault] | None:
        avail_map = {(item.var if isinstance(item, ir.Default) else item): item for item in available}
        result = []
        for req in required:
            var = req.var if isinstance(req, ir.Default) else req
            if var not in avail_map:
                return None
            # prefer the available default as it would've bubbled up and overridden
            # the required one, otherwise take the required
            result.append(avail_map[var] if isinstance(avail_map[var], ir.Default) else req)
        return result

    def safe_wrap(self, required_hoists:PySequence[ir.VarOrDefault]) -> ir.Task:
        first = self.items[0]
        if len(self.items) == 1 and isinstance(first, ir.Logical):
            merged = self.try_merge_hoists(required_hoists, first.hoisted)
            if merged is not None:
                return f.logical(list(first.body), merged)
        return f.logical(list(self.items), required_hoists)

    def clone(self):
        return CompilerContext(self.compiler, self)


class Compiler():
    def __init__(self):
        self.types:dict[Concept, ir.ScalarType] = {}
        self.name_to_type:dict[str, ir.Type] = {}
        self.relations:dict[Relationship|Concept|RelationshipRef, ir.Relation] = {}

    #--------------------------------------------------
    # Type/Relation conversion
    #--------------------------------------------------

    def to_annos(self, item:Concept|Relationship|Fragment) -> list[ir.Annotation]:
        annos = []
        items = item._annotations
        for item in items:
            if isinstance(item, Expression):
                annos.append(f.annotation(self.to_relation(item._op), item._params))
            elif isinstance(item, Relationship):
                annos.append(f.annotation(self.to_relation(item), []))
            else:
                raise ValueError(f"Cannot convert {type(item).__name__} to annotation")
        return annos

    def to_type(self, concept:Concept) -> ir.ScalarType:
        if concept not in self.types:
            if concept._name in types.builtin_scalar_types_by_name:
                self.types[concept] = types.builtin_scalar_types_by_name[concept._name]
            else:
                parent_types = [self.to_type(parent) for parent in concept._extends]
                self.types[concept] = f.scalar_type(concept._name, parent_types, annos=self.to_annos(concept))
            self.name_to_type[concept._name] = self.types[concept]
        return self.types[concept]

    def to_relation(self, item:Concept|Relationship|RelationshipRef) -> ir.Relation:
        if item not in self.relations:
            if isinstance(item, Concept):
                fields = [f.field(item._name.lower(), self.to_type(item))]
                relation = f.relation(item._name, fields, annos=self.to_annos(item))
            elif isinstance(item, Relationship):
                if item._ir_relation:
                    relation = item._ir_relation
                else:
                    fields = []
                    for cur in item._field_refs:
                        assert isinstance(cur._thing, Concept)
                        fields.append(f.field(to_name(cur), self.to_type(cur._thing)))
                    relation = f.relation(item._name, fields, annos=self.to_annos(item))
            elif isinstance(item, RelationshipRef):
                relation = self.to_relation(item._relationship)
            self.relations[item] = relation
            return relation
        else:
            return self.relations[item]

    #--------------------------------------------------
    # Model
    #--------------------------------------------------

    @roots(enabled=False)
    def model(self, model:Model) -> ir.Model:
        rules = []
        with debugging.span("rule_batch"):
            for rule in _global_roots:
                if not rule._model or rule._model == model:
                    meta = rule._meta if isinstance(rule, Fragment) else {}
                    with debugging.span("rule", dsl=str(rule), **with_source(rule), meta=meta) as rule_span:
                        rule_ir = self.compile_task(rule)
                        rules.append(rule_ir)
                        rule_span["metamodel"] = str(rule_ir)
        for concept in model.concepts.values():
            if concept not in self.types:
                self.to_type(concept)
                self.to_relation(concept)
        for relation in model.relationships:
            if relation not in self.relations:
                self.to_relation(relation)
        root = f.logical(rules)
        engines = ordered_set()
        relations = OrderedSet.from_iterable(self.relations.values())
        types = OrderedSet.from_iterable(self.types.values())
        return f.model(engines, relations, types, root)

    #--------------------------------------------------
    # Compile
    #--------------------------------------------------

    @roots(enabled=False)
    def compile_task(self, thing:Expression|Fragment) -> ir.Task:
        if isinstance(thing, (Expression, Match, Union)):
            return self.root_expression(thing)
        elif isinstance(thing, Fragment):
            return self.fragment(thing)

    #--------------------------------------------------
    # Root expression
    #--------------------------------------------------

    @roots(enabled=False)
    def root_expression(self, item:Expression) -> ir.Task:
        ctx = CompilerContext(self)
        self.update(item, ctx)
        return f.logical(list(ctx.items))

    #--------------------------------------------------
    # Fragment
    #--------------------------------------------------

    @roots(enabled=False)
    def fragment(self, fragment:Fragment, parent_ctx:CompilerContext|None=None, into_vars:list[ir.Var] = []) -> ir.Task:
        ctx = CompilerContext(self, parent_ctx)
        if fragment._require:
            self.require(fragment, fragment._require, ctx)
        else:
            self.where(fragment, fragment._where, ctx)
            self.define(fragment, fragment._define, ctx)
            self.select(fragment, fragment._select, ctx)
        return f.logical(list(ctx.items), ctx.into_vars, annos=self.to_annos(fragment))

    def where(self, fragment:Fragment, items:PySequence[Expression], ctx:CompilerContext):
        for item in items:
            self.lookup(item, ctx)

    def select(self, fragment:Fragment, items:PySequence[Expression], ctx:CompilerContext):
        if not items:
            return

        fields = []
        for ix, item in enumerate(items):
            keys = find_keys(item)
            for key in keys:
                self.lookup(key, ctx)
            sub_ctx = ctx.clone()
            raw_v = self.lookup(item, sub_ctx)
            if not isinstance(raw_v, list):
                raw_v = [raw_v]
            if len(sub_ctx.items) >= 1:
                ctx.add(sub_ctx.safe_wrap([ir.Default(v, None) for v in raw_v if isinstance(v, ir.Var)]))

            for v in raw_v:
                name = f"v{len(fields)}"
                if isinstance(item, Alias):
                    name = item._name
                elif isinstance(v, ir.Var):
                    name = v.name
                if ctx.into_vars:
                    ctx.add(f.lookup(builtins.eq, [ctx.into_vars[ix], v]))
                else:
                    fields.append((name, v))
        if fields:
            ctx.add(f.output(fields))

    def require(self, fragment:Fragment, items:PySequence[Expression], ctx:CompilerContext):
        domain_ctx = ctx.clone()
        self.where(fragment, fragment._where, domain_ctx)
        domain_vars = OrderedSet.from_iterable(flatten(list(domain_ctx.value_map.values())))
        to_hoist = OrderedSet()
        checks = []
        for item in items:
            req_ctx = domain_ctx.clone()
            self.lookup(item, req_ctx)
            req_body = f.logical(list(req_ctx.items))

            err_ctx = domain_ctx.clone()
            item_str = item._pprint() if isinstance(item, Producer) else str(item)
            keys = {to_name(k): k for k in find_keys(item)}
            source = item._source if hasattr(item, "_source") else fragment._source
            e = Error.new(message=f"Requirement not met: {item_str}", **keys, _source=source, _model=fragment._model)
            self.update(e, err_ctx)
            err_body = f.logical(list(err_ctx.items))
            checks.append(f.check(req_body, err_body))

            # find vars that overlap between domain and check/error and hoist them
            all_values = flatten(list(req_ctx.value_map.values()) + list(err_ctx.value_map.values()))
            to_hoist.update(domain_vars & OrderedSet.from_iterable(all_values))

        domain = f.logical(list(domain_ctx.items), list(to_hoist))
        req = f.require(domain, checks)
        ctx.add(req)

    def define(self, fragment:Fragment, items:PySequence[Expression], ctx:CompilerContext):
        if len(items) == 1:
            self.update(items[0], ctx)
            return

        for item in items:
            sub_ctx = ctx.clone()
            self.update(item, sub_ctx)
            if len(sub_ctx.items) > 1:
                ctx.add(f.logical(list(sub_ctx.items)))
            elif len(sub_ctx.items) == 1:
                ctx.add(sub_ctx.items[0])

    #--------------------------------------------------
    # Lookup
    #--------------------------------------------------

    def lookup(self, item:Any, ctx:CompilerContext) -> ir.Value|list[ir.Var]:
        if isinstance(item, ConceptExpression):
            assert isinstance(item._op, Concept)
            relation = self.to_relation(item._op)
            (ident, kwargs) = item._params

            rels = {self.to_relation(getattr(item._op, k)): unwrap_list(self.lookup(v, ctx))
                    for k, v in kwargs.items()}

            # If this is a member lookup, check that the identity is a member
            # and add all the kwargs as lookups
            if isinstance(item, ConceptMember):
                out = self.lookup(ident, ctx)
                assert isinstance(out, ir.Var)
                ctx.add(f.lookup(relation, [out]))
                for k, v in rels.items():
                    assert not isinstance(v, list)
                    ctx.add(f.lookup(k, [out, v]))
                return out

            # otherwise we have to construct one
            if ident is not None:
                rels[relation] = self.lookup(ident, ctx)
            out = ctx.to_value(item)
            assert isinstance(out, ir.Var)
            ctx.add(f.construct(out, rels))
            return out

        elif isinstance(item, Expression):
            params = [self.lookup(p, ctx) for p in item._params]
            relation = self.to_relation(item._op)
            ctx.add(f.lookup(relation, flatten(params)))
            return params[-1]

        elif isinstance(item, Concept):
            v = ctx.to_value(item)
            if not item._isa(Primitive):
                assert isinstance(v, ir.Var)
                relation = self.to_relation(item)
                ctx.add(f.lookup(relation, [v]))
            return v

        elif isinstance(item, (Relationship, RelationshipRef)):
            params = item._field_refs
            if item._parent:
                params = [item._parent] + params[1:]
            return self.lookup(item(*params), ctx)

        elif isinstance(item, RelationshipFieldRef):
            rel = item._relationship
            params = list(rel._field_refs)
            if item._parent:
                params = [item._parent] + params[1:]
            self.lookup(rel(*params), ctx)
            return self.lookup(params[item._field_ix], ctx)

        elif isinstance(item, Ref):
            if item._no_lookup:
                return ctx.to_value(item)

            root = item._thing
            prev_mapping = ctx.to_value(root)
            out = ctx.to_value(item)
            ctx.map_var(root, out)
            self.lookup(root, ctx)
            ctx.map_var(root, prev_mapping)
            return out

        elif isinstance(item, Alias):
            return self.lookup(item._thing, ctx)

        elif isinstance(item, Aggregate):
            relation = self.to_relation(item._op)
            assert relation.fields[0].name == "projection", "Aggregate structure has changed"

            # group
            group = [self.lookup(g, ctx) for g in item._group]
            group = [item for item in flatten(group) if isinstance(item, ir.Var)]

            # Agg context
            agg_ctx = ctx.clone()
            out = agg_ctx.to_value(item)
            assert isinstance(out, ir.Var)

            # additional wheres
            self.where(item._where, item._where._where, agg_ctx)

            # raw_args
            arg_count = len(relation.fields) - 3 # skip projection, group, and result
            raw_args = flatten([self.lookup(a, agg_ctx) for a in item._args])

            # the projection includes all keys for the args
            projection = flatten([self.lookup(key, agg_ctx) for key in find_keys(item._args)])
            # the projection is also all raw_args that aren't consumed by the agg
            projection += raw_args[:-arg_count] if arg_count else raw_args
            projection = list(dict.fromkeys([item for item in projection if isinstance(item, ir.Var)]))

            # agg args + result var
            args = raw_args[-arg_count:] if arg_count else []
            args.append(out)

            # add the aggregation
            ir_agg = f.aggregate(relation, projection, group, args)
            final_ctx = ctx.clone()
            if agg_ctx.items:
                internal = set(raw_args + projection) - set(flatten(list(ctx.value_map.values())))
                hoisted = [ir.Default(v, None) for v in internal if isinstance(v, ir.Var)]
                final_ctx.add(f.logical(list(agg_ctx.items), list(hoisted)))
            final_ctx.add(ir_agg)
            ctx.add(f.logical(list(final_ctx.items), [out]))
            return out

        elif isinstance(item, Not):
            not_ctx = ctx.clone()
            for a in item._args:
                self.lookup(a, not_ctx)
            ctx.add(f.not_(f.logical(list(not_ctx.items))))

        elif isinstance(item, Quantifier):
            agg_ctx = ctx.clone()
            self.where(item._where, item._where._where, agg_ctx)
            args = [self.lookup(a, agg_ctx) for a in item._args]
            args = [item for item in flatten(args) if isinstance(item, ir.Var)]
            body = f.logical(list(agg_ctx.items))
            if isinstance(item, Exists):
                ctx.add(f.exists(args, body))
            elif isinstance(item, Forall):
                ctx.add(f.for_all(args, body))

        elif isinstance(item, Fragment):
            if item._is_where_only():
                for where in item._where:
                    self.lookup(where, ctx)
                return None

            sub_ctx = ctx.clone()
            ctx.add(self.fragment(item, sub_ctx))
            if len(ctx.into_vars) == 1:
                return ctx.into_vars[0]
            elif len(ctx.into_vars) > 1:
                return ctx.into_vars
            elif len(item._select) == 1:
                return sub_ctx.to_value(item._select[0])
            elif len(item._select) > 1:
                return flatten([sub_ctx.to_value(s) for s in item._select])

        elif isinstance(item, (Match, Union)):
            branches = []
            vars = []
            if item._is_select:
                vars = ctx.value_map.get(item)
                if not vars:
                    vars = [f.var(f"v{i}") for i in range(item._ret_count)]
                    ctx.map_var(item, vars)
                assert isinstance(vars, list)
                for branch in item._args:
                    branch_ctx = ctx.clone()
                    branch_ctx.into_vars = vars
                    v = self.lookup(branch, branch_ctx)
                    if not isinstance(v, list):
                        v = [v]
                    for var, ret in zip(vars, v):
                        if var is not ret:
                            branch_ctx.add(f.lookup(builtins.eq, [var, ret]))
                    branches.append(branch_ctx.safe_wrap(vars))
            else:
                for branch in item._args:
                    branch_ctx = ctx.clone()
                    self.update(branch, branch_ctx)
                    branches.append(branch_ctx.safe_wrap([]))
            if isinstance(item, Union):
                ctx.add(f.union(branches, vars))
            else:
                ctx.add(f.match(branches, vars))

            return vars or None

        elif isinstance(item, BranchRef):
            vars = ctx.value_map.get(item._match)
            if not vars:
                self.lookup(item._match, ctx)
                vars = ctx.value_map.get(item._match)
            assert isinstance(vars, list)
            return vars[item._ix]

        elif isinstance(item, Group):
            for g in item._group:
                self.lookup(g, ctx)

        elif isinstance(item, Distinct):
            vs = [self.lookup(v, ctx) for v in item._args]
            return flatten(vs)

        elif isinstance(item, Data):
            refs = [item._row_id] + [i._ref for i in item._cols]
            ctx.add(f.data(item._data, flatten([self.lookup(v, ctx) for v in refs])))
            return

        elif isinstance(item, DataColumn):
            self.lookup(item._data, ctx)
            return ctx.to_value(item._ref)

        elif isinstance(item, (int, float, str, date, datetime)):
            return item

        elif item is None:
            return None

        elif isinstance(item, (ir.Var, ir.Literal)):
            return item

        elif hasattr(item, "_compile_lookup"):
            return item._compile_lookup(self, ctx)

        else:
            raise ValueError(f"Cannot lookup {item}, {type(item)}")

    #--------------------------------------------------
    # Update
    #--------------------------------------------------

    def update(self, item:Expression|Match|Union, ctx:CompilerContext) -> ir.Value|list[ir.Var]:
        if isinstance(item, ConceptExpression):
            assert isinstance(item._op, Concept)
            relation = self.to_relation(item._op)
            (ident, kwargs) = item._params
            out = ctx.to_value(item)
            assert isinstance(out, ir.Var)
            rels = {self.to_relation(getattr(item._op, k)): unwrap_list(self.lookup(v, ctx))
                    for k, v in kwargs.items()}

            # if this is a member lookup, then our out var is just the identity
            # passed in
            if isinstance(item, ConceptMember):
                out = self.lookup(ident, ctx)
                assert not isinstance(out, list)
                ctx.map_var(item, out)
            # otherwise we have to construct one
            else:
                construct_rels = rels.copy()
                if ident is not None:
                    construct_rels[relation] = self.lookup(ident, ctx)
                ctx.add(f.construct(out, construct_rels))

            # derive the membership and all the relationships
            ctx.add(f.derive(relation, [out]))
            for k, v in rels.items():
                assert not isinstance(v, list)
                ctx.add(f.derive(k, [out, v]))
            return out

        elif isinstance(item, Expression) and item._op is Relationship.builtins["="]:
            if isinstance(item._params[0], (Relationship, RelationshipRef)):
                return self.update(item._params[0](item._params[1]), ctx)
            elif isinstance(item._params[1], (Relationship, RelationshipRef)):
                return self.update(item._params[1](item._params[0]), ctx)
            elif isinstance(item._params[0], RelationshipFieldRef) or isinstance(item._params[1], RelationshipFieldRef):
                raise ValueError("Cannot set fields of a multi-field relationship individually")
            else:
                raise ValueError("Cannot set a non-relationship via ==")

        elif isinstance(item, Expression):
            params = flatten([self.lookup(p, ctx) for p in item._params])
            relation = self.to_relation(item._op)
            ctx.add(f.derive(relation, params))
            return params[-1]

        elif isinstance(item, Fragment):
            self.lookup(item, ctx)

        elif isinstance(item, (Match, Union)):
            self.lookup(item, ctx)

        elif hasattr(item, "_compile_update"):
            return item._compile_update(self, ctx)

        else:
            raise ValueError(f"Cannot update {item}")

__all__ = ["select", "where", "require", "define", "distinct", "per", "count", "sum", "min", "max", "avg"]

#--------------------------------------------------
# Todo
#--------------------------------------------------
"""
- Syntax
    ✔ construct
    ✔ static data handling
    ✔ Fix fragments to not be chained
    ✔ Extends
    ✔  Quantifiers
        ✔ not
        ✔ exists
        ✔ forall
    ✔ Aggregates
    ✔ Require
    ✘ Multi-step chaining
    ✔ ref
    ✔ alias
    ✔ match
    ✔ union
    ✔ capture all rules
    ✔ implement aliasing
    ✔ support defining relationships via madlibs Relationship("{Person} was born on {birthday:Date}")
    ✔ distinct
    ☐ nested fragments
    ✔  handle relationships with multiple name fields being accessed via prop:
        Package.shipment = Relationship("{Package} in {Shipment} on {Date}")
        Package.shipment.date, Package.shipment.shipment, Package.shipment.package
    ☐  sources
        ☐  table
        ☐  csv

- Compilation
    ✔ simple expressions
    ✔ select
    ✔ then
    ✔ Quantifiers
        ✔ exists
        ✔ forall
        ✔ not
    ✔ Aggregates
        ✔ Determine agg keys from inputs
        ✔ Group
    ✔ Require
    ✔ Alias
    ✔ Ref
    ✔ Match
    ✔ Union
    ✔ whole model
    ✔ distinct
    ✔ add Else to hoists
    ✔ where(..).define(Person.coolness == 10)
    ☐ extends
        ☐ nominals
    ✔ have require find keys and return the keys in the error
    ☐ Match/union with multiple branch refs in a select, duplicates the whole match
    ☐ nested fragments

☐ Execution
    ✔ basic queries
    ✔ query when iterating over a select
    ☐ debugger hookup
    ☐ table sources
    ☐ graph index
    ☐ exports
    ☐ config overhaul

"""
