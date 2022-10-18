from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID
from expert_dollup.shared.database_services import QueryFilter
from .values_union import PrimitiveWithNoneUnion


@dataclass
class ProjectNode:
    id: UUID
    project_id: UUID
    type_path: List[UUID]
    type_id: UUID
    type_name: str
    path: List[UUID]
    value: PrimitiveWithNoneUnion
    label: str = ""

    @property
    def subpath(self):
        return [*self.path, self.id]

    @property
    def type_subpath(self):
        return [*self.type_path, self.type_id]


class ProjectNodeFilter(QueryFilter):
    id: Optional[UUID]
    project_id: Optional[UUID]
    type_id: Optional[UUID]
    path: Optional[List[UUID]]
    label: Optional[str]
    level: Optional[int]
    display_query_internal_id: Optional[UUID]


class ProjectNodeValues(QueryFilter):
    id: Optional[UUID]
    project_id: Optional[UUID]
    type_id: Optional[UUID]
    path: Optional[List[UUID]]
    label: Optional[str]
    value: PrimitiveWithNoneUnion
    level: Optional[int]
    display_query_internal_id: Optional[UUID]


@dataclass
class FieldUpdate:
    node_id: UUID
    value: PrimitiveWithNoneUnion


class NodePluckFilter(QueryFilter):
    ids: Optional[List[UUID]]
    type_ids: Optional[List[UUID]]
