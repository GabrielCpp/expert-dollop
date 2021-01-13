from expert_dollup.shared.modeling import CamelModel
from typing import List
from uuid import UUID
from datetime import datetime


class ProjectDefinitionDto(CamelModel):
    id: UUID
    name: str
    default_datasheet_id: UUID
    plugins: List[UUID]
