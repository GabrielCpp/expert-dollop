from uuid import UUID
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Union
from expert_dollup.shared.database_services import QueryFilter

LabelAttributeUnion = Union[bool, int, str, float, UUID]


@dataclass
class Label:
    id: UUID
    label_collection_id: UUID
    order_index: int
    attributes: Dict[str, LabelAttributeUnion] = field(default_factory=dict)


class LabelFilter(QueryFilter):
    id: Optional[UUID]
    label_collection_id: Optional[UUID]


class LabelPluckFilter(QueryFilter):
    ids: Optional[List[UUID]]