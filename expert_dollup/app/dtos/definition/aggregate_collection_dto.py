from uuid import UUID

from typing import List, Union
from expert_dollup.shared.starlette_injection import CamelModel
from .project_definition_node_dto import (
    IntFieldConfigDto,
    DecimalFieldConfigDto,
    StringFieldConfigDto,
    BoolFieldConfigDto,
    AggregateReferenceConfigDto,
    NodeReferenceConfigDto,
)
from .aggregate_dto import AggregateDto


class AggregateAttributeSchemaDto(CamelModel):
    name: str
    details: Union[
        IntFieldConfigDto,
        DecimalFieldConfigDto,
        StringFieldConfigDto,
        BoolFieldConfigDto,
        AggregateReferenceConfigDto,
        NodeReferenceConfigDto,
    ]


class AggregateCollectionDto(CamelModel):
    id: UUID
    project_definition_id: UUID
    name: str
    is_abstract: bool
    attributes_schema: List[AggregateAttributeSchemaDto]


class NewAggregateCollectionDto(CamelModel):
    name: str
    is_abstract: bool
    attributes_schema: List[AggregateAttributeSchemaDto]
