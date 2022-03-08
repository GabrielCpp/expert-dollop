from expert_dollup.shared.starlette_injection import CamelModel
from typing import Dict
from uuid import UUID
from datetime import datetime


class ElementPropertySchemaDto(CamelModel):
    value_validator: dict


class ProjectDefinitionDto(CamelModel):
    id: UUID
    name: str
    default_datasheet_id: UUID
    properties: Dict[str, ElementPropertySchemaDto]
    creation_date_utc: datetime
