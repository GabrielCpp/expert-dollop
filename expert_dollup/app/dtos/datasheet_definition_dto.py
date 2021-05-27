from uuid import UUID
from typing import Dict
from expert_dollup.shared.modeling import CamelModel


class ElementPropertySchemaDto(CamelModel):
    value_validator: dict


class DatasheetDefinitionDto(CamelModel):
    id: UUID
    name: str
    properties: Dict[str, ElementPropertySchemaDto]
