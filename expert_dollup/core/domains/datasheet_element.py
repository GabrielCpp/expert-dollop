from uuid import UUID
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter
from functools import lru_cache
from .values_union import PrimitiveUnion


@lru_cache(maxsize=1)
def zero_uuid() -> UUID:
    return UUID(int=0)


@dataclass
class DatasheetElement:
    datasheet_id: UUID
    element_def_id: UUID
    child_element_reference: UUID
    properties: Dict[str, PrimitiveUnion]
    original_datasheet_id: UUID
    creation_date_utc: datetime

    @property
    def report_dict(self) -> dict:
        return {
            **self.properties,
            "element_def_id": self.element_def_id,
            "child_element_reference": self.child_element_reference,
            "original_datasheet_id": self.original_datasheet_id,
        }


@dataclass(init=False)
class DatasheetElementId(QueryFilter):
    datasheet_id: UUID
    element_def_id: UUID
    child_element_reference: UUID


class DatasheetElementFilter(QueryFilter):
    datasheet_id: Optional[UUID]
    element_def_id: Optional[UUID]
    child_element_reference: Optional[UUID]
    original_datasheet_id: Optional[UUID]
    creation_date_utc: Optional[datetime]


class DatasheetElementValues(QueryFilter):
    datasheet_id: Optional[UUID]
    element_def_id: Optional[UUID]
    child_element_reference: Optional[UUID]
    properties: Optional[Dict[str, PrimitiveUnion]]
    original_datasheet_id: Optional[UUID]
    creation_date_utc: Optional[datetime]


class DatasheetElementPluckFilter(QueryFilter):
    element_def_ids: List[UUID]