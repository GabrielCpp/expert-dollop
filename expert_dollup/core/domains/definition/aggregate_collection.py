from uuid import UUID
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Union, Optional, List
from expert_dollup.shared.database_services import QueryFilter
from .project_definition_node import (
    IntFieldConfig,
    DecimalFieldConfig,
    StringFieldConfig,
    BoolFieldConfig,
    AggregateReferenceConfig,
    NodeReferenceConfig,
)
from .aggregate import Aggregate


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
    attributes_schema: Dict[str, AggregateAttributeSchema] = field(default_factory=list)


@dataclass
class Aggregation:
    collection: AggregateCollection
    aggregates: List[Aggregate] = field(default_factory=list)


@dataclass
class NewAggregateCollection:
    name: str
    is_abstract: bool
    attributes_schema: List[AggregateAttributeSchema] = field(default_factory=list)


class AggregateCollectionFilter(QueryFilter):
    id: Optional[UUID]
    project_definition_id: Optional[UUID]
    name: Optional[str]
