from expert_dollup.shared.starlette_injection import CamelModel
from uuid import UUID
from typing import Optional
from .definition import ProjectDefinitionNodeDto


class ProjectNodeMetaStateDto(CamelModel):
    is_visible: bool
    selected_child: Optional[UUID]


class ProjectNodeMetaDto(CamelModel):
    project_id: UUID
    type_id: UUID
    state: ProjectNodeMetaStateDto
    definition: ProjectDefinitionNodeDto
