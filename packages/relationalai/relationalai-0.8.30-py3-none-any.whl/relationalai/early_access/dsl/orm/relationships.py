from collections import OrderedDict
from typing import Optional, Any

from relationalai.early_access.builder import Relationship as QBRelationship
from relationalai.early_access.builder.builder import Concept, type_from_type_str
from relationalai.early_access.dsl.core.utils import generate_stable_uuid
from relationalai.early_access.metamodel.util import OrderedSet


class Relation(QBRelationship):

    def __init__(self, model, reading:Any, part_of, relation_name: Optional[str] = None):
        super().__init__(reading, short_name=relation_name if relation_name else "", model=model.qb_model())
        self._dsl_model = model
        self._dsl_model._add_relation(self)
        self._part_of = part_of
        self._roles = []
        for idx, field in enumerate(self._fields):
            self._roles.append(Role(type_from_type_str(model.qb_model(), field.type_str), part_of, idx))

    def guid(self):
        return generate_stable_uuid(self._name)

    def arity(self):
        return len(self._fields)

    def binary(self):
        return self.arity() == 2

    def first(self):
        return self._roles[0]

    def alt(self, reading:Any, relation_name: Optional[str] = None):
        return self._part_of.add_relation(reading, relation_name)


class Relationship:

    def __init__(self, model, reading:Any, relation_name: Optional[str] = None):
        self._model = model
        self._relations = OrderedSet()
        self._readings_map = OrderedDict()
        # use the first reading as relationship name
        self._name = reading
        rel = self.add_relation(reading, relation_name)
        self._roles = []
        for r in rel._roles:
            self._roles.append(r)

    def add_relation(self, reading:Any, relation_name: Optional[str] = None) -> Relation:
        # todo: create a new Relation for now. Once QB will have `alt` API we can reuse it.
        rel = Relation(self._model, reading, self, relation_name)
        self._relations.add(rel)
        self._readings_map[reading] = rel
        return rel

    def arity(self):
        return len(self._roles)

    def guid(self):
        return generate_stable_uuid(self._name)

class Role:
    _sibling: Optional['Role'] = None

    def __init__(self, concept:Concept, part_of, pos, name:Optional[str] = None):
        self._concept = concept
        self._part_of = part_of
        self._pos = pos
        self._name = name

    def guid(self):
        return generate_stable_uuid(f"{self._pos}_{self._part_of.guid()}")

    def name(self) -> Optional[str]:
        return self._name

    def player(self) -> Concept:
        return self._concept

    def sibling(self):
        if self._part_of.arity() == 2 and not self._sibling:
            roles = self._part_of._roles
            sibling = roles[1] if self == roles[0] else roles[0]
            self._sibling = sibling
        return self._sibling

    @property
    def part_of(self):
        return self._part_of

    @part_of.setter
    def part_of(self, rel):
        if self._part_of is not None and self._part_of != rel:
            raise ValueError(f"Role is already part of another relationship: {self._part_of}")
        self._part_of = rel