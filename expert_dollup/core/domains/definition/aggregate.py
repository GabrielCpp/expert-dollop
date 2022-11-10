from uuid import UUID
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Union
from typing_extensions import TypeAlias
from decimal import Decimal
from expert_dollup.shared.database_services import QueryFilter
from ..values_union import PrimitiveWithReferenceUnion


@dataclass
class AggregateAttribute:
    name: str
    is_readonly: bool
    value: PrimitiveWithReferenceUnion


@dataclass
class Aggregate:
    id: UUID
    project_definition_id: UUID
    collection_id: UUID
    ordinal: int
    name: str
    is_extendable: bool
    attributes: Dict[str, AggregateAttribute] = field(default_factory=dict)

    def get_attribute(self, name: str):
        if name == "id":
            return self.id

        return self.attributes[name]

    @property
    def report_dict(self) -> dict:
        return {
            "id": self.id,
            "ordinal": self.ordinal,
            "name": self.name,
            "is_collection": self.is_extendable,
        }


@dataclass
class NewAggregate:
    ordinal: int
    name: str
    is_extendable: bool
    attributes: List[AggregateAttribute]


class AggregateFilter(QueryFilter):
    id: Optional[UUID]
    project_definition_id: Optional[UUID]
    collection_id: Optional[UUID]
    ordinal: Optional[int]
    name: Optional[str]
