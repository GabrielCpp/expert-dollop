from uuid import UUID
from expert_dollup.shared.modeling import CamelModel
from pydantic import Field
from typing import Dict
from .project_definition_node_dto import ValueUnionDto


class LabelDto(CamelModel):
    id: UUID
    label_collection_id: UUID
    order_index: int
    properties: Dict[str, ValueUnionDto] = Field(default_factory=dict)
    aggregates: Dict[str, UUID] = Field(default_factory=dict)
