from dataclasses import dataclass
from typing import List, Optional, Union
from uuid import UUID
from expert_dollup.shared.database_services import QueryFilter
from .project_definition_node import ValueUnion
from .project_container_meta import ProjectContainerMeta


@dataclass
class ProjectContainer:
    id: UUID
    project_id: UUID
    type_path: List[UUID]
    type_id: UUID
    path: List[UUID]
    value: ValueUnion

    @property
    def subpath(self):
        return [*self.path, self.id]

    @property
    def type_subpath(self):
        return [*self.type_path, self.type_id]


class ProjectContainerFilter(QueryFilter):
    id: Optional[UUID]
    project_id: Optional[UUID]
    type_id: Optional[UUID]
    path: Optional[List[UUID]]
    value: ValueUnion
