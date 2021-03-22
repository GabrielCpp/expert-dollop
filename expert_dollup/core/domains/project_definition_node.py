from dataclasses import dataclass
from uuid import UUID
from typing import Optional, List
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter


@dataclass
class ProjectDefinitionContainerNode:
    id: UUID
    project_def_id: UUID
    name: str
    is_collection: bool
    instanciate_by_default: bool
    order_index: int
    config: dict
    value_type: str
    default_value: Optional[dict]
    path: List[UUID]

    @property
    def subpath(self):
        return [*self.path, self.id]


class ProjectDefinitionContainerNodeFilter(QueryFilter):
    id: Optional[UUID]
    project_def_id: Optional[UUID]
    name: Optional[str]
    is_collection: Optional[bool]
    instanciate_by_default: Optional[bool]
    order_index: Optional[int]
    config: Optional[dict]
    value_type: Optional[str]
    default_value: Optional[dict]
    path: Optional[List[UUID]]


