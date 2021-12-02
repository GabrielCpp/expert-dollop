from uuid import UUID
from dataclasses import dataclass, field
from typing import Dict, Union
from .project_definition_node import JsonSchema


@dataclass
class CollectionAggregate:
    from_collection: str


@dataclass
class DatasheetAggregate:
    from_datasheet: str


AcceptedAggregateUnion = Union[CollectionAggregate, DatasheetAggregate]


@dataclass
class LabelCollection:
    id: UUID
    datasheet_definition_id: UUID
    name: str
    properties_schema: Dict[str, JsonSchema] = field(default_factory=dict)
    accepted_aggregates: Dict[str, AcceptedAggregateUnion] = field(default_factory=dict)
