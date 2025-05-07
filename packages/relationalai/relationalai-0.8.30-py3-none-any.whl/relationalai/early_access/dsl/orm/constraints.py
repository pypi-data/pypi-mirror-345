from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic, Union

from relationalai.early_access.dsl.core.utils import generate_stable_uuid
from relationalai.early_access.dsl.orm.relationships import Role


class Constraint(ABC):
    @abstractmethod
    def validate(self, ontology) -> bool:
        """Validate the constraint against the ontology."""

    @abstractmethod
    def _unique_name(self) -> str:
        """Validate the constraint against the ontology."""

    @abstractmethod
    def roles(self) -> list[Role]:
        """Return the roles of the constraint."""

    @abstractmethod
    def desugar(self):
        """Declare QB constraints"""

    def guid(self):
        return generate_stable_uuid(self._unique_name())

    def __eq__(self, other):
        if isinstance(other, Constraint):
            return self.guid() == other.guid()
        return False

    def __hash__(self):
        return hash(self.guid())


class Unique(Constraint):
    def __init__(self, *roles:Role, is_preferred_identifier=False):
        self._roles = list(roles)
        self.is_preferred_identifier = is_preferred_identifier

    def roles(self):
        return self._roles

    def validate(self, ontology) -> bool:
        # Implement uniqueness validation logic here
        return True

    def desugar(self):
        # todo: Implement QB representation
        pass

    def _unique_name(self) -> str:
        return f'Unique{"".join(role.guid() for role in self._roles)}'

    def __repr__(self):
        return f'Unique(({", ".join(role.guid() for role in self._roles)}), preferred_identifier={self.is_preferred_identifier})'

class Mandatory(Constraint):
    def __init__(self, role: Role):
        self.role = role

    def roles(self):
        return [self.role]

    def validate(self, ontology) -> bool:
        # Implement mandatory validation logic here
        return True

    def desugar(self):
        # todo: Implement QB representation
        pass

    def _unique_name(self) -> str:
        return f'Mandatory{self.role.guid()}'

    def __repr__(self):
        return f'Mandatory({self.role.guid()})'

# Role value constraint
T = TypeVar('T', int, float, str)

class Range(Generic[T]):

    def __init__(self, start: Optional[T], end: Optional[T]):
        if start is None and end is None:
            raise ValueError("'start' and 'end' cannot be None")
        if start is not None and end is not None:
            if type(start) is not type(end):
                raise TypeError("'start' and 'end' must be of same type")
            if start > end: # type: ignore[reportOperatorIssue]
                raise ValueError("'start' must be less than 'end'")
        self._start = start
        self._end = end

    def matches(self, value: T) -> bool:
        if self._start is not None and value < self._start:
            return False
        if self._end is not None and value > self._end:
            return False
        return True

    def type(self):
        if self._start is not None:
            return type(self._start)
        else:
            return type(self._end)

    def __repr__(self):
        return f"Range({self._start}, {self._end})"

    @staticmethod
    def between(start: T, end: T):
        return Range(start, end)

    @staticmethod
    def to_value(value: T):
        return Range(None, value)

    @staticmethod
    def from_value(value: T):
        return Range(value, None)

class RoleValueConstraint(Constraint, Generic[T]):
    def __init__(self, role: Role, values: List[Union[T, Range[T]]]):
        self._role = role
        self._values = values

    def roles(self):
        return [self._role]

    def values(self):
        return self._values

    def validate(self, ontology) -> bool:
        # Implement role value validation logic here
        return True

    def desugar(self):
        # todo: Implement QB representation
        pass

    def _unique_name(self) -> str:
        return f'RoleValueConstraint{self._role.guid()}'

    def role(self):
        return self._role

    def __repr__(self):
        return f'RoleValueConstraint({self._role.guid()}, values={self._values})'
