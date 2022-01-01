from uuid import UUID
from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime
from .values_union import PrimitiveUnion
from expert_dollup.shared.database_services import QueryFilter


@dataclass
class DatasheetDefinitionElementProperty:
    is_readonly: bool
    value: PrimitiveUnion


@dataclass
class DatasheetDefinitionElement:
    id: UUID
    unit_id: str
    is_collection: bool
    datasheet_def_id: UUID
    order_index: int
    name: str
    default_properties: Dict[str, DatasheetDefinitionElementProperty]
    tags: List[UUID]
    creation_date_utc: datetime

    @property
    def report_dict(self):
        return {
            "id": self.id,
            "unit_id": self.unit_id,
            "is_collection": self.is_collection,
            "order_index": self.order_index,
            "name": self.name,
            "tags": self.tags,
        }


class DatasheetDefinitionElementFilter(QueryFilter):
    id: Optional[UUID]
    unit_id: Optional[str]
    is_collection: Optional[bool]
    datasheet_def_id: Optional[UUID]
    order_index: Optional[int]
    default_properties: Optional[DatasheetDefinitionElementProperty]
    tags: Optional[List[UUID]]
    creation_date_utc: Optional[datetime]
