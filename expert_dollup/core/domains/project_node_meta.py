from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from expert_dollup.shared.database_services import QueryFilter
from .project_definition_node import ProjectDefinitionNode


@dataclass
class ProjectNodeMetaState:
    is_visible: bool
    selected_child: Optional[UUID]


@dataclass
class ProjectNodeMeta:
    project_id: UUID
    type_id: UUID
    state: ProjectNodeMetaState
    definition: ProjectDefinitionNode


class ProjectNodeMetaFilter(QueryFilter):
    project_id: Optional[UUID]
    type_id: Optional[UUID]
    state: Optional[ProjectNodeMetaState]
    display_query_internal_id: Optional[UUID]
