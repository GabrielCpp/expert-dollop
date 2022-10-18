from uuid import UUID
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Union, Optional
from expert_dollup.shared.database_services import QueryFilter
from .project_definition_node import (
    IntFieldConfig,
    DecimalFieldConfig,
    StringFieldConfig,
    BoolFieldConfig,
    AggregateReferenceConfig,
)
from .aggregate import Aggregate


class NodeType(Enum):
    FORMULA = "FORMULA"
    FIELD = "FORMULA"
    SECTION = "SECTION"
    FORM = "FORM"
    SUB_SECTION = "SUB_SECTION"
    ROOT_SECTION = "ROOT_SECTION"


@dataclass
class NodeReferenceConfig:
    node_type: NodeTypeDto


@dataclass
class AggregateAttributeSchema:
    name: str
    details: Union[
        IntFieldConfig,
        DecimalFieldConfig,
        StringFieldConfig,
        BoolFieldConfig,
        AggregateReferenceConfig,
        NodeReferenceConfig,
    ]


@dataclass
class AggregateCollection:
    id: UUID
    project_definition_id: UUID
    name: str
    is_abstract: bool = False
    attributes_schema: List[AggregateAttributeSchema] = field(default_factory=list)


@dataclass
class Aggregation(AggregateCollection):
    aggregates: List[AggregateDto] = field(default_factory=list)


class AggregateCollectionFilter(QueryFilter):
    id: Optional[UUID]
    project_definition_id: Optional[UUID]
    name: Optional[str]
