from expert_dollup.shared.starlette_injection import CamelModel
from typing import List
from uuid import UUID
from datetime import datetime


class ProjectDefinitionDto(CamelModel):
    id: UUID
    name: str
    default_datasheet_id: UUID
    datasheet_def_id: UUID
