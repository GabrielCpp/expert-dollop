from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ProjectDto(BaseModel):
    id: UUID
    name: str
    is_staged: bool
    project_def_id: UUID
    datasheet_id: UUID
    owner_id: UUID
