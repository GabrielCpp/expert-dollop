from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from expert_dollup.shared.database_services import QueryFilter
from .project_definition_node import ProjectDefinitionNode


@dataclass
class ProjectContainerMetaState:
    is_visible: bool
    selected_child: Optional[UUID]


@dataclass
class ProjectContainerMeta:
    project_id: UUID
    type_id: UUID
    state: ProjectContainerMetaState
    definition: ProjectDefinitionNode


class ProjectContainerMetaFilter(QueryFilter):
    project_id: Optional[UUID]
    type_id: Optional[UUID]
