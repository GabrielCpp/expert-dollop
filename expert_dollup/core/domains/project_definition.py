from dataclasses import dataclass
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter
from .project_definition_node import JsonSchema


@dataclass
class ElementPropertySchema:
    value_validator: JsonSchema


@dataclass
class ProjectDefinition:
    id: UUID
    name: str
    default_datasheet_id: UUID
    properties: Dict[str, ElementPropertySchema]
    creation_date_utc: datetime


class ProjectDefinitionFilter(QueryFilter):
    id: Optional[UUID]
    name: Optional[str]
    default_datasheet_id: Optional[UUID]
    properties: Optional[Dict[str, ElementPropertySchema]]
    creation_date_utc: Optional[datetime]
