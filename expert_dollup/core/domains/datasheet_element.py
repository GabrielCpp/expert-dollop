from uuid import UUID
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DatasheetElement:
    datasheet_id: UUID
    element_def_id: UUID
    child_element_reference: UUID
    properties: dict
    original_datasheet_id: UUID
    creation_date_utc: datetime