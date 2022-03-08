from uuid import UUID
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Union
from decimal import Decimal
from expert_dollup.shared.database_services import QueryFilter

LabelAttributeUnion = Union[bool, int, str, Decimal, UUID]


@dataclass
class Label:
    id: UUID
    label_collection_id: UUID
    order_index: int
    name: str
    attributes: Dict[str, LabelAttributeUnion] = field(default_factory=dict)

    def get_attribute(self, name: str):
        if name == "id":
            return self.id

        return self.attributes[name]

    @property
    def report_dict(self) -> dict:
        return {
            **self.attributes,
            "id": self.id,
            "order_index": self.order_index,
            "name": self.name,
        }


class LabelFilter(QueryFilter):
    id: Optional[UUID]
    label_collection_id: Optional[UUID]


class LabelPluckFilter(QueryFilter):
    ids: Optional[List[UUID]]
