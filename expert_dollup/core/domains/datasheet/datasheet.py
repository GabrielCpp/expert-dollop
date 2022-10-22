from uuid import UUID
from dataclasses import dataclass
from typing import Optional, Dict
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter
from ..definition.aggregate_collection import AggregateAttributeSchema
from ..definition.aggregate import AggregateAttribute


@dataclass
class AggregateAttributeSchema:
    is_readonly: bool


@dataclass
class AggregateSchema:
    is_extendable: bool
    attributes_schema: Dict[str, AggregateAttributeSchema]


@dataclass
class Datasheet:
    id: UUID
    name: str
    project_definition_id: UUID
    from_abstract_collection: UUID
    from_datasheet_id: UUID
    attributes_schema: Dict[str, AggregateAttributeSchema]
    instances_schema: Dict[UUID, AggregateSchema]
    creation_date_utc: datetime


@dataclass
class CloningDatasheet:
    clone_name: str
    target_datasheet_id: UUID


class DatasheetFilter(QueryFilter):
    id: Optional[UUID]
    name: Optional[str]
    project_definition_id: Optional[UUID]
    from_abstract_collection: Optional[UUID]
    from_datasheet_id: Optional[UUID]
    creation_date_utc: Optional[datetime]
