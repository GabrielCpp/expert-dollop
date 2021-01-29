from expert_dollup.shared.modeling import CamelModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class ProjectDto(CamelModel):
    id: UUID
    name: str
    is_staged: bool
    project_def_id: UUID
    datasheet_id: UUID
