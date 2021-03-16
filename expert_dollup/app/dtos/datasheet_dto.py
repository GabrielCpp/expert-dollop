from uuid import UUID
from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from expert_dollup.shared.modeling import CamelModel
from expert_dollup.shared.database_services import QueryFilter


class NewDatasheetDto(CamelModel):
    id: UUID
    name: str
    is_staged: bool
    datasheet_def_id: UUID
    from_datasheet_id: UUID


class DatasheetUpdatableProperties(CamelModel):
    name: Optional[str]
    is_staged: Optional[bool]


class DatasheetUpdateDto(CamelModel):
    id: UUID
    updates: DatasheetUpdatableProperties


class DatasheetCloneTargetDto(CamelModel):
    target_datasheet_id: UUID
    new_name: str


class DatasheetDto(CamelModel):
    id: UUID
    name: str
    is_staged: bool
    datasheet_def_id: UUID
    from_datasheet_id: UUID
    creation_date_utc: datetime
