from expert_dollup.shared.starlette_injection import CamelModel
from typing import Dict, List
from uuid import UUID
from datetime import datetime


class ElementPropertySchemaDto(CamelModel):
    name: str
    value_validator: dict


class ProjectDefinitionDto(CamelModel):
    id: UUID
    name: str
    default_datasheet_id: UUID
    properties: List[ElementPropertySchemaDto]
    creation_date_utc: datetime


class NewDefinitionDto(CamelModel):
    name: str
