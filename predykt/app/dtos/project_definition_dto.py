from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime


class ProjectDefinitionDto(BaseModel):
    id: UUID
    name: str
    default_datasheet_id: UUID
    plugins: List[UUID]
