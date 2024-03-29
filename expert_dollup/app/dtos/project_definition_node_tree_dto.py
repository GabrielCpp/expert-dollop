from expert_dollup.shared.starlette_injection import CamelModel
from uuid import UUID
from typing import Optional, List
from datetime import datetime
from .project_definition_node_dto import ProjectDefinitionNodeDto


class ProjectDefinitionTreeNodeDto(CamelModel):
    definition: ProjectDefinitionNodeDto
    children: List["ProjectDefinitionTreeNodeDto"]


ProjectDefinitionTreeNodeDto.update_forward_refs()


class ProjectDefinitionNodeTreeDto(CamelModel):
    roots: List[ProjectDefinitionTreeNodeDto]
