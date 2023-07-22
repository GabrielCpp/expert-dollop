from expert_dollup.shared.starlette_injection import CamelModel
from typing import Dict, List
from uuid import UUID
from datetime import datetime


class ProjectDefinitionDto(CamelModel):
    id: UUID
    name: str
    creation_date_utc: datetime


class NewDefinitionDto(CamelModel):
    name: str
