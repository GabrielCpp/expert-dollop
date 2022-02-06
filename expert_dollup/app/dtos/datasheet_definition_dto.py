from uuid import UUID
from typing import Dict
from datetime import datetime
from expert_dollup.shared.starlette_injection import CamelModel


class ElementPropertySchemaDto(CamelModel):
    value_validator: dict


class DatasheetDefinitionDto(CamelModel):
    id: UUID
    name: str
    properties: Dict[str, ElementPropertySchemaDto]
    creation_date_utc: datetime
