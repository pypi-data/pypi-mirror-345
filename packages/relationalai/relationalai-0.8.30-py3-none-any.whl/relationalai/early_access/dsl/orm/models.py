from collections import OrderedDict
from typing import Optional, Any, List, Union, TypeVar

from relationalai.early_access.builder import Model as QBModel
from relationalai.early_access.builder import Relationship as QBRelationship
from relationalai.early_access.dsl.bindings.tables import Binding
from relationalai.early_access.dsl.bindings.tables import SnowflakeTable, CsvTable
from relationalai.early_access.dsl.codegen.weaver import Weaver
from relationalai.early_access.dsl.core.types.unconstrained import UnconstrainedValueType
from relationalai.early_access.dsl.core.utils import generate_stable_uuid, to_pascal_case
from relationalai.early_access.dsl.orm.constraints import Unique, Mandatory, RoleValueConstraint, Range
from relationalai.early_access.dsl.orm.relationships import Relationship, Relation
from relationalai.early_access.dsl.orm.types import Concept, EntityType, ValueType
from relationalai.early_access.dsl.snow.api import Executor
from relationalai.early_access.metamodel.util import OrderedSet

T = TypeVar('T', int, float, str)

class Model:
    def __init__(self, name: str, is_primary: bool = True):
        self.name = name
        self._qb_model = QBModel(name)
        self.is_primary = is_primary
        self._value_types = OrderedDict()
        self._entity_types = OrderedDict()
        self._relationships = OrderedDict()
        self._relations = OrderedDict()
        self._constraints = OrderedSet()
        self._entity_to_id_relationship = OrderedDict()
        self._bindable_tables = OrderedDict()
        self._bindings = []
        self._executor = Executor()
        self._weaver = Weaver(self)
        self._queries = OrderedSet()

    def guid(self):
        return generate_stable_uuid(self.name)

    def ValueType(self, name: str, extends: Optional['Concept']=None) -> ValueType:
        name = to_pascal_case(name)
        vt = ValueType(self, name, extends)
        self._validate_type_name(name)
        self._value_types[name] = vt
        if name not in self.qb_model().concepts:
            self.qb_model().concepts[name] = vt
        return vt

    def EntityType(self, name: str, extends:list['Concept'] = [], refmode: Optional[str] = None) -> EntityType:
        name = to_pascal_case(name)
        et = EntityType(self, name, extends, ref_schema_name=refmode)
        self._validate_type_name(name)
        self._entity_types[name] = et
        if name not in self.qb_model().concepts:
            self.qb_model().concepts[name] = et
        return et

    def Concept(self, name: str, extends: list['Concept'] = []) -> 'Concept':
        name = to_pascal_case(name)
        c = Concept(self, name, extends)
        if name not in self.qb_model().concepts:
            self.qb_model().concepts[name] = c
        self._validate_type_name(name)
        if c.is_value_type():
            self._value_types[name] = c
        else:
            self._entity_types[name] = c
        return c

    def qb_model(self):
        return self._qb_model

    def Relationship(self, reading: Any, relation_name: Optional[str] = None) -> QBRelationship:
        """
        Create a new relationship with the given reading.
        """
        relationship = Relationship(self, reading, relation_name=relation_name)
        self._add_relationship(relationship)
        return relationship._readings_map[reading]

    def constraint(self, constraint):
        # Generic constraint addition with validation
        self._constraints.add(constraint)
        constraint.desugar()

    def unique(self, *roles):
        self.constraint(Unique(*roles))

    def mandatory(self, role):
        self.constraint(Mandatory(role))

    def role_value_constraint(self, relation: Relation, values: List[Union[T, Range[T]]]):
        first_type = values[0].type() if isinstance(values[0], Range) else type(values[0])
        for v in values[1:]:
            t = v.type() if isinstance(v, Range) else type(v)
            if t != first_type:
                raise Exception("Values for role value constraint must have the same type.")
        if not relation.binary():
            raise Exception("The relation should be binary to apply role value constraint")
        role = relation.first()
        sibling_role = role.sibling()
        sibling = sibling_role.player()
        if sibling._is_primitive() or sibling.is_value_type():
            self.constraint(RoleValueConstraint(sibling_role, values))
        else:
            raise Exception("A role value constraint can only be applied to roles played by value types")

    def ref_scheme(self, *relations:Relation):
        self._validate_ref_scheme_input_relations(relations)
        if len(relations) == 1:
            # binary case, internal UC
            role = relations[0]._roles[1]
            self._internal_preferred_uc(role)
        else:
            roles = [rel._roles[1] for rel in relations]
            self._composite_preferred_uc(*roles)

    def _internal_preferred_uc(self, role):
        rel = role.part_of
        if rel.arity() != 2:
            raise Exception("The relationship should be binary to apply preferred identifier constraint")
        # mark the role as preferred identifier
        self.constraint(Unique(role, is_preferred_identifier=True))
        # mark the sibling role as mandatory and unique
        sibling = role.sibling()
        self.mandatory(sibling)
        self.unique(sibling)

    def _composite_preferred_uc(self, *roles):
        for role in roles:
            sibling = role.sibling()
            if not sibling:
                raise Exception("Composite preferred identifier constraint should be applied on binary relationships")
            self.mandatory(sibling)
            self.unique(sibling)
        self.constraint(Unique(*roles, is_preferred_identifier=True))

    @staticmethod
    def _validate_ref_scheme_input_relations(relations):
        if not relations:
            raise ValueError("ref_scheme requires at least one relation")
        ref_rel = relations[0]
        for rel in relations:
            if not isinstance(rel, QBRelationship):
                raise ValueError("ref_scheme can only be applied on Relation instances")
            if rel.arity() != 2:
                raise ValueError("ref_scheme can only be applied on binary relations")
            if rel.first().player()._id != ref_rel.first().player()._id:
                raise ValueError("For ref_scheme all relations must have the same role player in position 0")

    def lookup_concept(self, name) -> Optional['Concept']:
        name = to_pascal_case(name)
        if name in self._value_types:
            return self._value_types[name]
        if name in self._entity_types:
            return self._entity_types[name]
        return None

    def lookup_relationship(self, name) -> Optional['Relationship']:
        if name in self._relationships:
            return self._relationships[name]
        return None

    def constraints(self):
        """Getter for the _constraints property"""
        return self._constraints

    def queries(self):
        return self._queries

    def value_types(self):
        return list(self._value_types.values())

    def entity_types(self):
        return list(self._entity_types.values())

    def entity_types_map(self):
        return self._entity_types

    def relationships(self):
        return list(self._relationships.values())

    def relations(self):
        return list(self._relations.values())

    def bindable_tables(self):
        return self._bindable_tables

    def api(self):
        return self._executor

    def table(self, name: str) -> SnowflakeTable:
        metadata = self._executor.table_metadata(name)
        table = SnowflakeTable(metadata, self)
        self._bindable_tables[name] = table
        return table

    def csv_table(self, name: str, schema: dict[str, UnconstrainedValueType]) -> CsvTable:
        table = CsvTable(name, schema, self)
        self._bindable_tables[name] = table
        return table

    def binding(self, binding: Binding):
        self._bindings.append(binding)

    def generate_weaving_rules(self):
        self._weaver.generate()

    def _add_relationship(self, rel: 'Relationship'):
        self._validate_relationship_name(rel._name)
        self._relationships[rel._name] = rel

    def _add_relation(self, relation: Relation) -> Relation:
        if relation._id in self._relations:
            existed_relation = self._relations[relation._id]
            # todo: add validation that relations' signature is the same
            return existed_relation
        self._relations[relation._id] = relation
        return relation

    def _validate_type_name(self, name):
        if name in self._entity_types:
            raise Exception(
                f"The name '{name}' is used to declare an entity type.")
        if name in self._value_types:
            raise Exception(
                f"The name '{name}' is used to declare a value type.")

    def _validate_relationship_name(self, name):
        if name in self._relationships:
            raise Exception(
                f"The name '{name}' is used to declare a relationship.")
