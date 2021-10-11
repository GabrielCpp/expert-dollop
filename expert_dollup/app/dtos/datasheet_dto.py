from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime
from expert_dollup.shared.modeling import CamelModel
from pydantic import Field


class NewDatasheetDto(CamelModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    datasheet_definition_id: UUID
    from_datasheet_id: Optional[UUID] = None
    is_staged: bool = False


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
    from_datasheet_id: Optional[UUID]
    creation_date_utc: datetime
