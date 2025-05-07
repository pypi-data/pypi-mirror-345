from typing import Any, Optional

from relationalai.early_access.builder import Concept as QBConcept


class Concept(QBConcept):

    def __init__(self, model, name: str, extends: list[Any] = []):
        super().__init__(name, extends, model.qb_model())
        self._dsl_model = model

    def is_value_type(self) -> bool:
        if len(self._extends) == 1:
            ext_concept = self._extends[0]
            if ext_concept._is_primitive():
                return True
            else:
                return ext_concept.is_value_type()
        return False


class EntityType(Concept):

    def __init__(self, model, nm, extends: list[Concept] = [], ref_schema_name: Optional[str] = None):
        self._domain = extends
        super().__init__(model, nm, extends)
        self._ref_schema_name = ref_schema_name

    def qualified_name(self):
        return self._name

    def is_composite(self):
        return len(self._domain) > 1

    def ref_schema_name(self):
        return self._ref_schema_name

    def is_value_type(self) -> bool:
        return False


class ValueType(Concept):

    def __init__(self, model, nm, extends: Optional[Concept] = None):
        super().__init__(model, nm, [extends] if extends is not None else [])

    def is_value_type(self) -> bool:
        return True