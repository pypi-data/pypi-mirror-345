"""
Type inference for the IR.
"""
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Iterable, Union as PyUnion, Tuple, cast
from datetime import date, datetime
import networkx as nx

from relationalai.early_access.metamodel.util import OrderedSet, ordered_set
from relationalai.early_access.metamodel import ir, types, visitor, compiler

# Type System
# -----------
#
# Scalar types are either value types or entity types, not both.
# Value types (transitively) extend the built-in scalar types for which
# `is_value_base_type` holds.
# All other scalar types are entity types.
#
# Subtyping of scalar is declared explicitly in the model, currently as the
# `super_types` field in `ScalarType`, but this may change.
#
# The type system supports unions and tuples of types.
# Tuple types are covariant in their element types.
# Union types support the usual subtyping relation (for instance, a member of a
# union is a subtype of the union).
# We could, but currently do not, introduce common supertypes for unions.
#
# The `Any` type is used as a placeholder to mean "infer this type". `Any` is a
# scalar type.
# In particular, `Any` is not implicitly a supertype of any other type.
#
# List types are not allowed in the model and should have been rewritten to
# tuple types by the `RewriteListTypes` pass.
#
# Set types in the model indicate the multiplicity of the given field. They are
# not strictly types.
# For inference purposes, the element type is used as the type of the field,
# however when substituting inference results back into the model, the inferred
# type is wrapped in a `SetType`.
# Set types must be sets of scalar type (including `Any`).
#
# Type inference works as follows:
# - For each application of a relation:
#   - for input fields, bound the argument type by the field type (that is, arg
#     <: field; this is the standard rule for argument passing, types flow from
#     the argument to the field)
#   - for non-input fields (which could be input or output), equate the argument
#     type with the corresponding field type in the relation (= is more
#     efficient than adding two bounds: arg <: field and field <: arg)
# - For each variable, bound its type with its declared type.
# - For each field, bound its type with its declared type.
# - For default values, bound the variable type with the type of the default value.
# - These constraints build a graph of equivalence classes of nodes (fields and
# - vars). An edge a->b indicates that a is a subtype of b.
#   Each nodes has an associated set of upper and lower bounding scalar types.
# - Propagate upper bounds through the graph from supertype to subtype.
# - Propagate lower bounds through the graph from suptype to supertype.
# - Collapse cycles (SCCs) in the graph into an equivalence class.
# - For each equivalence class, union the upper bounds of all types in the
#   class. This is the inferred upper bound. Check that the inferred upper bound
#   of a node is a supertype of the all lower bounds of the node.
# - If the type of a field cannot be inferred to any type (as happens when the
#   field is not used in any application), equate the relation with other
#   relations of the same name and arity, if any. Then recompute the bound
#   again. This has the effect of treating relations of the same name and arity
#   as overloads of each other, but only when necessary.
# - Replace the types in the model with the intersection of the inferred upper
#   bound and the declared type. This strictly lowers types to be more precise.

@dataclass
class TypeVar:
    """A type variable."""
    # The node that this type variable is bound to.
    # Together with the index, this uniquely identifies the type variable.
    node: ir.Node = field(init=True)

    # The index of the field of the node, or 0.
    # Together with the node (id), this uniquely identifies the type variable.
    index: int = field(init=True)

    # The upper bound of the type variable.
    upper_bound: OrderedSet[ir.Type] = field(default_factory=OrderedSet, init=False, compare=False, hash=False, repr=False)
    # The lower bound of the type variable.
    lower_bound: OrderedSet[ir.Type] = field(default_factory=OrderedSet, init=False, compare=False, hash=False, repr=False)
    # Set of TypeVars that are supertypes of this type variable.
    node_super_types: OrderedSet["TypeVar"] = field(default_factory=OrderedSet, init=False, compare=False, hash=False, repr=False)

    # Union-find data structure.
    # The rank of the type variable.
    rank: int = field(default=0, init=False, compare=False, hash=False, repr=False)
    # The next type variable in the union-find data structure. If this is None, the type variable is the root of its union-find tree.
    next: Optional["TypeVar"] = field(default=None, init=False, compare=False, hash=False, repr=False)

    def __hash__(self) -> int:
        return hash((self.node.id, self.index))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TypeVar):
            return False
        return self.node.id == other.node.id and self.index == other.index

    def __str__(self) -> str:
        return f"{ir.node_to_string(self.node).strip()}{f'@{self.index}' if self.index >= 0 else ''} (id={self.node.id})"

    def find(self) -> "TypeVar":
        """Find the root of this type variable and perform path compression."""
        if self.next is None:
            return self
        self.next = self.next.find()
        return self.next

    def union(self, other: "TypeVar") -> "TypeVar":
        """Union this type variable with another, returning the root of the union."""
        top = self.find()
        bot = other.find()
        assert top.next is None
        assert bot.next is None
        if top == bot:
            return top
        if top.rank < bot.rank:
            top, bot = bot, top
        bot.next = top
        top.upper_bound.update(bot.upper_bound)
        top.lower_bound.update(bot.lower_bound)
        top.node_super_types.update(bot.node_super_types)
        bot.upper_bound.clear()
        bot.lower_bound.clear()
        bot.node_super_types.clear()
        assert self.find() == top
        assert other.find() == top
        return top

    @staticmethod
    def pretty_name(node: PyUnion[ir.Var, ir.Field], index: int, parent: Optional[ir.Node]) -> str:
        if isinstance(node, ir.Var):
            return f"Variable `{node.name}`"
        else:
            if index < 0:
                if isinstance(parent, ir.Relation):
                    return f"Field `{node.name}` of relation `{parent.name}`"
                else:
                    return f"Field `{node.name}`"
            else:
                if isinstance(parent, ir.Relation):
                    return f"Element {index} of field `{node.name}` of relation `{parent.name}`"
                else:
                    return f"Element {index} of field `{node.name}`"

@dataclass
class TypeError:
    """A type inference error."""
    msg: str
    node: ir.Node

Typeable = PyUnion[ir.Value, ir.Type, ir.Var, ir.Field, TypeVar]

@dataclass
class TypeEnv:
    """Environment for type inference that tracks type bounds for each node."""

    # The model being type-checked.
    model: ir.Model

    # Diagnostics. For now, this is just strings.
    diags: List[TypeError]

    # Maps node ids (and tuple index, as needed) to the type variables for their types.
    type_vars: Dict[Tuple[int, int], TypeVar]

    # How verbose to be with debug info, 0 for off.
    verbosity: int

    # Should we perform stricter checks on the inferred types.
    strict: bool

    def __init__(self, model: ir.Model, strict: bool, verbosity: int=0):
        super().__init__()
        self.model = model
        self.diags = []
        self.type_vars = {}
        self.strict = strict
        self.verbosity = verbosity

    def _complain(self, node: ir.Node, msg: str):
        """Report an error."""
        self.diags.append(TypeError(msg, node))

    def get_type_var(self, node: ir.Node, index: int = -1) -> TypeVar:
        key = (node.id, index)
        if key not in self.type_vars:
            self.type_vars[key] = TypeVar(node, index)
        tv = self.type_vars[key]
        assert tv.node == node
        assert tv.index == index
        return tv

    def _get_type(self, t: PyUnion[ir.Literal, ir.PyValue]) -> Optional[ir.Type]:
        if t is None:
            return types.Null
        elif isinstance(t, str):
            return types.String
        elif isinstance(t, bool):
            return types.Bool
        elif isinstance(t, int):
            return types.Int
        elif isinstance(t, float):
            return types.Float
        elif isinstance(t, date):
            return types.Date
        elif isinstance(t, datetime):
            return types.DateTime
        elif isinstance(t, ir.Literal):
            return t.type
        else:
            raise ValueError(f"Unexpected value {t} of type {type(t)}")

    def add_bound(self, lower: Typeable, upper: Typeable):
        if upper is None or isinstance(upper, (ir.Literal, str, bool, int, float, date, datetime)):
            t = self._get_type(upper)
            assert t is not None
            self.add_bound(lower, t)
        elif lower is None or isinstance(lower, (ir.Literal, str, bool, int, float, date, datetime)):
            t = self._get_type(lower)
            assert t is not None
            self.add_bound(t, upper)
        elif isinstance(lower, (ir.Var, ir.Field)):
            x = self.get_type_var(lower)
            self.add_bound(x, upper)
        elif isinstance(upper, (ir.Var, ir.Field)):
            x = self.get_type_var(upper)
            self.add_bound(lower, x)
        elif isinstance(upper, ir.UnionType):
            for t in upper.types:
                self.add_bound(lower, t)
        elif isinstance(lower, ir.UnionType):
            for t in lower.types:
                self.add_bound(t, upper)
        elif isinstance(lower, TypeVar):
            if isinstance(upper, ir.Type):
                if not types.is_any(upper):
                    lower.find().upper_bound.add(upper)
            elif isinstance(upper, TypeVar):
                lower.find().node_super_types.add(upper.find())
            else:
                raise ValueError(f"Unexpected types {type(lower)} and {type(upper)}")
        elif isinstance(lower, ir.Type):
            if isinstance(upper, ir.Type):
                if lower == upper:
                    return
                elif types.is_subtype(lower, upper):
                    return
                else:
                    self.diags.append(TypeError(f"Type {ir.type_to_string(lower)} is not a subtype of {ir.type_to_string(upper)}", lower))
            elif isinstance(upper, TypeVar):
                if not types.is_null(lower):
                    upper.find().lower_bound.add(lower)
            else:
                raise ValueError(f"Unexpected types {type(lower)} and {type(upper)}")
        else:
            raise ValueError(f"Unexpected types {type(lower)} and {type(upper)}")

    def add_equality(self, t1: Typeable, t2: Typeable):
        if t1 is None:
            self.add_equality(types.Null, t2)
        elif t2 is None:
            self.add_equality(t1, types.Null)
        elif isinstance(t1, (ir.Literal, str, bool, int, float, date, datetime)):
            t = self._get_type(t1)
            self.add_equality(t, t2)
        elif isinstance(t2, (ir.Literal, str, bool, int, float, date, datetime)):
            t = self._get_type(t2)
            self.add_equality(t1, t)
        elif isinstance(t1, (ir.Var, ir.Field)):
            x = self.get_type_var(t1)
            self.add_equality(x, t2)
        elif isinstance(t2, (ir.Var, ir.Field)):
            x = self.get_type_var(t2)
            self.add_equality(t1, x)
        elif isinstance(t1, ir.Type):
            if isinstance(t2, ir.Type):
                self.add_bound(t1, t2)
                self.add_bound(t2, t1)
            elif isinstance(t2, TypeVar):
                if not types.is_any(t1):
                    t2.find().upper_bound.add(t1)
                if not types.is_null(t1):
                    t2.find().lower_bound.add(t1)
            else:
                raise ValueError(f"Cannot equate nodes {t1} and {t2}")
        elif isinstance(t1, TypeVar):
            if isinstance(t2, TypeVar):
                t1.union(t2)
            elif isinstance(t2, ir.Type):
                if not types.is_any(t2):
                    t1.find().upper_bound.add(t2)
                if not types.is_null(t2):
                    t1.find().lower_bound.add(t2)
            else:
                raise ValueError(f"Cannot equate nodes {t1} and {t2}")
        else:
            raise ValueError(f"Cannot equate nodes {t1} and {t2}")

    def _collapse_node_supertype_cycles(self):
        # Create a directed graph from the node_super_types relationships
        G = nx.DiGraph()

        for v in self._tyvars():
            v = v.find()
            for w in v.node_super_types:
                w = w.find()
                G.add_edge(v, w)

        # Equate all type vars in the same SCC.
        for scc in nx.strongly_connected_components(G):
            if len(scc) > 1:
                cycle = list(scc)
                for t in cycle[1:]:
                    cycle[0].union(t)

    def dump(self):
        for v in self._tyvars():
            if v != v.find():
                print(f"{v} == {v.find()}")

        seen = set()
        for v in self._tyvars():
            v = v.find()
            if v.node.id in seen:
                continue
            seen.add(v.node.id)
            for w in v.node_super_types:
                print(f"{v} --> {w}")

        for v in self._tyvars():
            v = v.find()
            if v.lower_bound:
                print(f"{' | '.join(ir.value_to_string(t) for t in v.lower_bound)} <: {v}")
            if v.upper_bound:
                print(f"{v} <: {' | '.join(ir.value_to_string(t) for t in v.upper_bound)}")

    def type_bounds_compatible(self, tv1: TypeVar, tv2: TypeVar) -> bool:
        # Check that two type variables have compatible bounds.
        for lb in tv1.lower_bound:
            for ub in tv2.upper_bound:
                if not types.is_subtype(lb, ub):
                    return False
        for lb in tv2.lower_bound:
            for ub in tv1.upper_bound:
                if not types.is_subtype(lb, ub):
                    return False
        # TODO: not sure if this is needed. Leave out for now.
        # Check that all upper bounds are either value types or entity types, not both.
        if False:
            if all(types.is_value_type(ub) for ub in tv1.upper_bound) != all(types.is_value_type(ub) for ub in tv2.upper_bound):
                return False
            if all(not types.is_value_type(ub) for ub in tv1.upper_bound) != all(not types.is_value_type(ub) for ub in tv2.upper_bound):
                return False
        return True

    def compute_type_from_bounds(self, node: PyUnion[ir.Var, ir.Field], bound: OrderedSet[ir.Type]) -> Optional[ir.Type]:
        # Union all the types in the upper bound and intersect with the lower bound.
        # If we have {Any} in the union, change all the types to Set types.
        # Discard Any from the union.
        assert all(isinstance(t, (ir.ScalarType, ir.TupleType)) for t in bound), f"Bound {bound} contains non-scalar or non-tuple types."
        not_any = [t for t in bound if not types.is_any(t)]
        if not not_any:
            return None
        union = types.union(*not_any)
        return union

    def compute_type(self, tv: TypeVar, node: PyUnion[ir.Var, ir.Field], index: int, parent: ir.Node) -> ir.Type:
        root = tv.find()

        # Union all the types in the upper bound and intersect with the lower bound.
        # If we have {Any} in the union, change all the types to Set types.
        # Discard Any from the union.
        upper = self.compute_type_from_bounds(node, root.upper_bound)

        if upper is None:
            # We don't have any constraints that bound the type from above.
            if self.strict:
                self._complain(node, f"Could not infer a type for {ir.node_to_string(node).strip()}")
            return cast(ir.Type, types.Any)

        for lower in root.lower_bound:
            # TODO
            # Disable the check that the lower bound is satisfied.
            # If we don't declare all the subtype relationships, we'll end up with errors here.
            # Strict models should check this.
            # if not self.strict:
            #     continue
            if not types.is_subtype(lower, upper):
                name = TypeVar.pretty_name(node, index, parent)
                self._complain(node, f"{name} must be a supertype of {ir.type_to_string(lower)}, but has type {ir.type_to_string(upper)} instead.")

        return cast(ir.Type, upper)

    def _propagate_bounds(self):
        """Propagate bounds along node_super_types edges until a fixpoint is reached."""
        worklist = ordered_set(*self._tyvars())
        while worklist:
            sub = worklist.pop()
            sub = sub.find()
            for sup in sub.node_super_types:
                sup = sup.find()
                # Propagate upper bounds downward from supertype to subtype.
                n = len(sub.upper_bound)
                sub.upper_bound |= sup.upper_bound
                if n != len(sub.upper_bound):
                    worklist.add(sub)
                # Propagate lower bounds upward from subtype to supertype.
                n = len(sup.lower_bound)
                sup.lower_bound |= sub.lower_bound
                if n != len(sup.lower_bound):
                    worklist.add(sup)

    def _tyvars(self) -> Iterable[TypeVar]:
        """Return all the type variables in the graph."""
        return self.type_vars.values()

    def _equivalent_tyvars(self, tv: TypeVar) -> Iterable[TypeVar]:
        """Return the set of type variables that are equivalent to the given type variable."""
        tv = tv.find()
        return [v for v in self._tyvars() if v.find() == tv]

    def _unify_overloaded_relations(self):
        """Unify relations with the same name and arity that have compatible types."""
        worklist = ordered_set(*self._tyvars())
        while worklist:
            v = worklist.pop()
            v = v.find()

            # Non-strict models:
            # If there is no bound for the field, equate the relation with other relations of the same name
            # that have compatible types.
            # Then add back to the worklist all type variables in the relations.
            if not v.upper_bound:
                fields = []
                # If a tyvar has no upper bound, find all fields in the same equivalence class and
                # equate their enclosing relations.

                # 1. Get all the fields in the equivalence class.
                for x in self._equivalent_tyvars(v):
                    if isinstance(x.node, ir.Field):
                        fields.append(x.node)

                # 2. Get their enclosing relations.
                enclosing_relations = ordered_set()
                for f in fields:
                    # First find the enclosing relation of this field.
                    for r in self.model.relations:
                        for f2 in r.fields:
                            if f2.id == f.id:
                                enclosing_relations.add(r)
                                break

                # 3. Equate the relations with the same name and arity that have compatible types.
                changed = False
                for enclosing_relation in enclosing_relations:
                    for r in self.model.relations:
                        if r.id == enclosing_relation.id:
                            continue
                        if r.name == enclosing_relation.name and len(r.fields) == len(enclosing_relation.fields):
                            # Check for compatible types.
                            all_compat = True
                            for (f1, f2) in zip(r.fields, enclosing_relation.fields):
                                tv1 = self.get_type_var(f1).find()
                                tv2 = self.get_type_var(f2).find()
                                if self.type_bounds_compatible(tv1, tv2):
                                    all_compat = False
                                    break
                            if all_compat:
                                for (f1, f2) in zip(r.fields, enclosing_relation.fields):
                                    tv1 = self.get_type_var(f1).find()
                                    tv2 = self.get_type_var(f2).find()
                                    self.add_equality(tv1, tv2)
                                    assert tv1.find() == tv2.find()
                                    tv = tv1.find()
                                    # Enqueue all tyvars in the equivalence class of the fields.
                                    for x in self._equivalent_tyvars(tv):
                                        worklist.add(x)
                                    changed = True
                if changed:
                    # TODO This should be done incrementally on the new equivalents relations in the worklist.
                    self._collapse_node_supertype_cycles()
                    # There's no need to propagate bounds again since no changes
                    # are made to node_super_types.

    def solve(self):
        """Solve the type constraints."""

        if self.verbosity:
            print("\n")
            if self.verbosity > 1:
                ir.dump(self.model)
            else:
                print(self.model)

            print("\n")
            print("Constraints before solving:")
            self.dump()

        # Collapse all the node_super_types cycles into equalities.
        self._collapse_node_supertype_cycles()
        # Propagate bounds along node_super_types edges.
        self._propagate_bounds()
        # Unify overloaded relations.
        self._unify_overloaded_relations()

        if self.verbosity:
            print("\n")
            print("Constraints after solving:")
            self.dump()


@dataclass
class SubstituteTypes(visitor.DeprecatedPass):
    """
    A visitor that substitutes types back into the model.
    """
    env: TypeEnv = field(init=True)
    strict: bool = field(init=True)

    def handle_var(self, node: ir.Var, parent: ir.Node) -> ir.Var:
        x = self.env.get_type_var(node)
        t = self.env.compute_type(x, node, x.index, parent)
        if t is not None and not types.is_null(t):
            if isinstance(t, ir.UnionType):
                for t2 in t.types:
                    if not isinstance(t2, ir.ScalarType):
                        self.env._complain(node, f"Variable {node.name} inferred to be a non-scalar type {t2}. Variables must have scalar type.")
            elif not isinstance(t, ir.ScalarType):
                self.env._complain(node, f"Variable {node.name} inferred to be a non-scalar type {t}. Variables must have scalar type.")
            # Substitute the intersection of the inferred type with the declared type.
            new_type = SubstituteTypes._lower_type(node.type, t)
            return ir.Var(new_type, node.name)
        else:
            if self.strict:
                self.env._complain(node, f"Could not infer a type for variable {node.name}")
            return node

    def handle_field(self, node: ir.Field, parent: ir.Node) -> ir.Field:
        # Substitute the intersection of the inferred type with the declared type.
        changed = False
        if isinstance(node.type, ir.TupleType):
            new_types = []
            for i in range(len(node.type.types)):
                name = TypeVar.pretty_name(node, i, parent)
                x = self.env.get_type_var(node, i)
                t = self.env.compute_type(x, node, i, parent)
                if t is not None and not types.is_null(t):
                    if isinstance(t, ir.UnionType):
                        for t2 in t.types:
                            if not isinstance(t2, ir.ScalarType):
                                self.env._complain(node, f"{name} is inferred to be a non-scalar type {t2}. Variables must have scalar type.")
                    elif not isinstance(t, ir.ScalarType):
                        self.env._complain(node, f"{name} is inferred to be a non-scalar type {t}. Variables must have scalar type.")
                    new_type = SubstituteTypes._lower_type(node.type.types[i], t)
                    changed = True
                else:
                    if self.strict:
                        lower_name = name[0].lower() + name[1:]
                        self.env._complain(node, f"Could not infer a type for {lower_name}")
                    new_type = node.type.types[i]
                new_types.append(new_type)
            new_type = ir.TupleType(tuple(new_types))
        else:
            name = TypeVar.pretty_name(node, -1, parent)
            x = self.env.get_type_var(node)
            t = self.env.compute_type(x, node, x.index, parent)
            if t is not None and not types.is_null(t):
                if isinstance(t, ir.UnionType):
                    for t2 in t.types:
                        if not isinstance(t2, ir.ScalarType):
                            self.env._complain(node, f"{name} inferred to be a non-scalar type {t2}. Variables must have scalar type.")
                elif not isinstance(t, ir.ScalarType):
                    self.env._complain(node, f"{name} inferred to be a non-scalar type {t}. Variables must have scalar type.")
                new_type = SubstituteTypes._lower_type(node.type, t)
                changed = True
            else:
                if self.strict:
                    lower_name = name[0].lower() + name[1:]
                    self.env._complain(node, f"Could not infer a type for {lower_name}")
                new_type = node.type
        if changed:
            return ir.Field(node.name, new_type, node.input)
        else:
            return node

    # Intersect the declared type with the inferred type, special casing set types.
    @staticmethod
    def _lower_type(declared: ir.Type, inferred: ir.Type) -> ir.Type:
        if isinstance(declared, ir.SetType):
            assert isinstance(inferred, ir.ScalarType)
            return ir.SetType(SubstituteTypes._lower_type(declared.element_type, inferred))
        else:
            return types.intersect(declared, inferred)


@dataclass
class CollectTypeConstraints(visitor.DAGVisitor):
    """
    A visitor that collects type constraints on a model.
    """
    def __init__(self, env: TypeEnv):
        super().__init__()
        self.env = env

    def visit_scalartype(self, node: ir.Type, parent: Optional[ir.Node]=None):
        # Do not recurse.
        pass

    def visit_listtype(self, node: ir.ListType, parent: Optional[ir.Node]=None):
        # Do not recurse.
        pass

    def visit_settype(self, node: ir.SetType, parent: Optional[ir.Node]=None):
        # Do not recurse.
        pass

    def visit_uniontype(self, node: ir.UnionType, parent: Optional[ir.Node]=None):
        # Do not recurse.
        pass

    def visit_field(self, node: ir.Field, parent: Optional[ir.Node]=None):
        # Do not constrain field types to be <: Any.
        if isinstance(node.type, ir.SetType):
            if not types.is_any(node.type.element_type):
                self.env.add_bound(node, node.type.element_type)
        elif isinstance(node.type, ir.TupleType):
            for i in range(len(node.type.types)):
                x = self.env.get_type_var(node, i)
                if not types.is_any(node.type.types[i]):
                    self.env.add_bound(x, node.type.types[i])
        elif isinstance(node.type, ir.UnionType):
            for t in node.type.types:
                if not types.is_any(t):
                    self.env.add_bound(node, t)
        elif isinstance(node.type, ir.ScalarType):
            if not types.is_any(node.type):
                self.env.add_bound(node, node.type)
        # Do not recurse. No need to visit the type.
        pass

    def visit_var(self, node: ir.Var, parent: Optional[ir.Node]=None):
        # Do not constrain field types to be <: Any.
        if isinstance(node.type, ir.UnionType):
            for t in node.type.types:
                if not types.is_any(t):
                    self.env.add_bound(node, t)
        elif isinstance(node.type, ir.ScalarType):
            if not types.is_any(node.type):
                self.env.add_bound(node, node.type)
        # Do not recurse. No need to visit the type.
        pass

    def visit_default(self, node: ir.Default, parent: Optional[ir.Node]=None):
        # The variable's type should be a supertype of the default value.
        self.env.add_bound(node.value, node.var)
        # Recurse to add the constraints on the variable.
        return super().visit_default(node, parent)

    def visit_literal(self, node: ir.Literal, parent: Optional[ir.Node]=None):
        # Do not recurse. No need to visit the type.
        pass

    def visit_loop(self, node: ir.Loop, parent: Optional[ir.Node]=None):
        # The iterator should be a number.
        self.env.add_bound(node.iter, types.Number)
        return super().visit_loop(node, parent)

    def visit_update(self, node: ir.Update, parent: Optional[ir.Node]=None):
        if len(node.args) == len(node.relation.fields):
            # We have update R(x,y,z) where R is declared (t,u,v)
            # Bound each arg by the declared type of the field.
            for f, arg in zip(node.relation.fields, node.args):
                if f.input:
                    # Flow from argument to input field.
                    self.env.add_bound(arg, f)
                else:
                    # Flow from argument to field, and back.
                    self.env.add_equality(arg, f)
        return super().visit_update(node, parent)

    def visit_annotation(self, node: ir.Annotation, parent: Optional[ir.Node]=None):
        # Do not recurse. No need to visit the relation again.
        pass

    def visit_lookup(self, node: ir.Lookup, parent: Optional[ir.Node]=None):
        if len(node.args) == len(node.relation.fields):
            # We have lookup R(x,y,z) where R is declared (t,u,v)
            # Bound each arg by the declared type of the field.
            for f, arg in zip(node.relation.fields, node.args):
                if f.input:
                    # Flow from argument to input field.
                    self.env.add_bound(arg, f)
                else:
                    # Flow from argument to field, and back.
                    self.env.add_equality(arg, f)
        return super().visit_lookup(node, parent)

    def visit_aggregate(self, node: ir.Aggregate, parent: Optional[ir.Node]=None):
        agg = node.aggregation

        if len(agg.fields) < 3:
            return

        projection = agg.fields[0]
        group = agg.fields[1]

        inputs = []
        outputs = []
        for f in agg.fields[2:]:
            if f.input:
                inputs.append(f)
            else:
                outputs.append(f)

        # Now let's wire up the types.

        # Projection field.
        if isinstance(projection.type, ir.ScalarType):
            # In this case, we know the arity is 1, we just need to constrain the projection variables to be the same as the projection field types.
            if len(node.projection) == 1:
                self.env.add_equality(projection.type, node.projection[0])
        elif isinstance(projection.type, ir.TupleType):
            # In this case, we know the arity, we just need to constrain the projection variables to be the same as the projection field types.
            if len(node.projection) == len(projection.type.types):
                for i in range(len(node.projection)):
                    f = self.env.get_type_var(projection, i)
                    a = node.projection[i]
                    self.env.add_equality(f, a)

        # Group field.
        if isinstance(group.type, ir.ScalarType):
            # In this case, we know the arity is 1, we just need to constrain the group variables to be the same as the group field types.
            if len(node.group) == 1:
                self.env.add_equality(group.type, node.group[0])
        elif isinstance(group.type, ir.TupleType):
            # In this case, we know the arity, we just need to constrain the group variables to be the same as the group field types.
            if len(node.group) == len(group.type.types):
                for i in range(len(node.group)):
                    f = self.env.get_type_var(group, i)
                    a = node.group[i]
                    self.env.add_equality(f, a)

        # Inputs and outputs.
        if len(node.args) == len(inputs) + len(outputs):
            for a, f in zip(node.args[0:len(inputs)], inputs):
                # Flow from argument to input field.
                self.env.add_bound(a, f)

            for a, f in zip(node.args[len(inputs):], outputs):
                # Flow from argument to field, and back.
                self.env.add_equality(a, f)

        return super().visit_aggregate(node, parent)


@dataclass
class Typer(compiler.Pass):
    """
    A pass that performs type inference on a model.
    The pass also checks that the model is well-formed.
    Diagnostics are reported for ill-formed or ill-typed models.

    The main idea is to traverse the model and collect type constraints.
    These are then solved and substituted back into the model.
    """

    # Should we perform stricter checks on the inferred types?
    strict: bool = field(default=False, init=False)

    # How verbose to be with debug output, 0 is off.
    verbosity: int = field(default=0, init=False)

    def rewrite(self, model: ir.Model, cache) -> ir.Model:
        if self.verbosity:
            print("Initial model:")
            if self.verbosity > 1:
                ir.dump(model)
            else:
                print(model)

        # Type inference.
        env = TypeEnv(model, self.strict, self.verbosity)
        collector = CollectTypeConstraints(env)
        model.accept(collector)

        if self.verbosity:
            print("Constraints:")
            env.dump()

        env.solve()

        # Substitute the types back into the model.
        subst = SubstituteTypes(env, self.strict)
        model2 = subst.walk(model)

        # Assert that there are no type errors
        if env.diags:
            error_count = len(env.diags)
            error_header = "TYPE ERROR\n" if error_count == 1 else f"{error_count} TYPE ERRORS\n"
            formatted_errors = [error_header] + [f"* (Node id={env.diags[i].node.id}) {env.diags[i].msg}" for i in range(error_count)] + ["-----"] + [str(model)]
            raise Exception("\n".join(formatted_errors))

        if self.verbosity:
            print("After substitution:")
            if self.verbosity > 1:
                ir.dump(model)
            else:
                print(model2)

        return model2
