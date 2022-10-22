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
            **self.attributes,
            "id": self.id,
            "ordinal": self.ordinal,
            "name": self.name,
        }
