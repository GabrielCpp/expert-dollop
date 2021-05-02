from expert_dollup.shared.modeling import CamelModel
from typing import List
from uuid import UUID
from .project_container_dto import ProjectContainerDto
from .project_definition_node_dto import ProjectDefinitionNodeDto
from .project_container_meta_dto import ProjectContainerMetaStateDto


class ProjectContainerTreeTypeNodeDto(CamelModel):
    definition: ProjectDefinitionNodeDto
    state: ProjectContainerMetaStateDto
    nodes: List["ProjectContainerTreeNodeDto"]


class ProjectContainerTreeNodeDto(CamelModel):
    node: ProjectContainerDto
    children: List[ProjectContainerTreeTypeNodeDto]


ProjectContainerTreeTypeNodeDto.update_forward_refs()


class ProjectContainerTreeDto(CamelModel):
    roots: List[ProjectContainerTreeTypeNodeDto]
