from dataclasses import dataclass
from uuid import UUID
from typing import Optional, List
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter


@dataclass
class ProjectDefinitionContainer:
    id: UUID
    project_def_id: UUID
    name: str
    is_collection: bool
    instanciate_by_default: bool
    order_index: int
    custom_attributes: dict
    value_type: str
    default_value: Optional[dict]
    path: List[UUID]


class ProjectDefinitionContainerFilter(QueryFilter):
    id: Optional[UUID]
    project_def_id: Optional[UUID]
    name: Optional[str]
    is_collection: Optional[bool]
    instanciate_by_default: Optional[bool]
    order_index: Optional[int]
    custom_attributes: Optional[dict]
    value_type: Optional[str]
    default_value: Optional[dict]
    path: Optional[List[UUID]]
