from expert_dollup.shared.modeling import CamelModel
from uuid import UUID
from typing import Optional
from .project_definition_node_dto import ProjectDefinitionNodeDto


class ProjectContainerMetaStateDto(CamelModel):
    is_visible: bool
    selected_child: Optional[UUID]


class ProjectContainerMetaDto(CamelModel):
    project_id: UUID
    type_id: UUID
    state: ProjectContainerMetaStateDto
    definition: ProjectDefinitionNodeDto
