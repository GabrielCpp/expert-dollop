from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from datetime import datetime


class ProjectDefinitionContainerDto(BaseModel):
    id: UUID
    project_def_id: UUID
    name: str
    is_collection: bool
    instanciate_by_default: bool
    custom_attributes: dict
    value_type: str
    default_value: Optional[dict]
    path: List[UUID]
