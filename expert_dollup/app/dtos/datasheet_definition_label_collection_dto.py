from uuid import UUID
from expert_dollup.shared.modeling import CamelModel
from pydantic import Field
from typing import Dict
from .project_definition_node_dto import ValueUnionDto


class LabelCollectionDto(CamelModel):
    id: UUID
    datasheet_definition_id: UUID
    name: str
    default_properties: Dict[str, ValueUnionDto] = Field(default_factory=dict)
