from expert_dollup.shared.modeling import CamelModel
from uuid import UUID
from typing import Optional, List
from datetime import datetime
from .project_definition_node_dto import ProjectDefinitionContainerNodeDto


class ProjectDefinitionContainerNodeTreeNodeDto(CamelModel):
    definition: ProjectDefinitionContainerNodeDto
    children: List["ProjectDefinitionContainerNodeTreeNodeDto"]


class ProjectDefinitionContainerNodeTreeDto(CamelModel):
    roots: List[ProjectDefinitionContainerNodeTreeNodeDto]
