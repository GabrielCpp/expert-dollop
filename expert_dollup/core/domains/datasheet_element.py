from uuid import UUID
from typing import Optional, Dict, Union
from dataclasses import dataclass
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter


@dataclass
class DatasheetElement:
    datasheet_id: UUID
    element_def_id: UUID
    child_element_reference: UUID
    properties: Dict[str, Union[float, str, bool]]
    original_datasheet_id: UUID
    creation_date_utc: datetime


@dataclass(init=False)
class DatasheetElementId(QueryFilter):
    datasheet_id: UUID
    element_def_id: UUID
    child_element_reference: UUID


class DatasheetElementFilter(QueryFilter):
    datasheet_id: Optional[UUID]
    element_def_id: Optional[UUID]
    child_element_reference: Optional[UUID]
    properties: Optional[Dict[str, Union[float, str, bool]]]
    original_datasheet_id: Optional[UUID]
    creation_date_utc: Optional[datetime]
