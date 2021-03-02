from uuid import UUID
from typing import List, Union, Optional
from dataclasses import dataclass
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter


@dataclass
class DatasheetDefinitionElementProperty:
    is_readonly: bool
    value: Union[float, str, bool]


@dataclass
class DatasheetDefinitionElement:
    id: UUID
    unit_id: UUID
    is_collection: bool
    datasheet_def_id: UUID
    order_index: int
    default_properties: DatasheetDefinitionElementProperty
    tags: List[UUID]
    creation_date_utc: datetime


class DatasheetDefinitionElementFilter(QueryFilter):
    id: Optional[UUID]
    unit_id: Optional[UUID]
    is_collection: Optional[bool]
    datasheet_def_id: Optional[UUID]
    order_index: Optional[int]
    default_properties: Optional[DatasheetDefinitionElementProperty]
    tags: Optional[List[UUID]]
    creation_date_utc: Optional[datetime]
