from uuid import UUID
from enum import Enum
from typing import List, Union
from expert_dollup.shared.starlette_injection import CamelModel
from .project_definition_node_dto import (
    IntFieldConfigDto,
    DecimalFieldConfigDto,
    StringFieldConfigDto,
    BoolFieldConfigDto,
    AggregateReferenceConfigDto,
)
from .aggregate_dto import AggregateDto


class NodeTypeDto(Enum):
    FORMULA = "FORMULA"
    FIELD = "FORMULA"
    SECTION = "SECTION"
    FORM = "FORM"
    SUB_SECTION = "SUB_SECTION"
    ROOT_SECTION = "ROOT_SECTION"


class NodeReferenceConfigDto(CamelModel):
    node_type: NodeTypeDto


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


class AggregationDto(AggregateCollectionDto):
    aggregates: List[AggregateDto]


class NewAggregateCollectionDto(CamelModel):
    name: str
    attributes_schema: List[AggregateAttributeSchemaDto]
