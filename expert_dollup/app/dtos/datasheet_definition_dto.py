from uuid import UUID
from typing import Dict
from expert_dollup.shared.modeling import CamelModel


class DatasheetDefinitionDto(CamelModel):
    id: UUID
    name: str
    element_properties_schema: Dict[str, dict]
