from expert_dollup.shared.starlette_injection import CamelModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class ProjectDetailsInputDto(CamelModel):
    name: str
    project_def_id: UUID
    datasheet_id: UUID


class ProjectDetailsDto(CamelModel):
    id: UUID
    name: str
    is_staged: bool
    project_def_id: UUID
    datasheet_id: UUID
    creation_date_utc: datetime
