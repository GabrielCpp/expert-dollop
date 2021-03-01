from uuid import UUID
from typing import List, Union
from dataclasses import dataclass
from datetime import datetime


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
