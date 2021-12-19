from expert_dollup.shared.starlette_injection import CamelModel
from typing import List
from uuid import UUID
from .project_node_dto import ProjectNodeDto
from .project_definition_node_dto import ProjectDefinitionNodeDto
from .project_node_meta_dto import ProjectNodeMetaStateDto


class ProjectNodeTreeTypeNodeDto(CamelModel):
    definition: ProjectDefinitionNodeDto
    state: ProjectNodeMetaStateDto
    nodes: List["ProjectNodeTreeNodeDto"]


class ProjectNodeTreeNodeDto(CamelModel):
    node: ProjectNodeDto
    children: List[ProjectNodeTreeTypeNodeDto]


ProjectNodeTreeTypeNodeDto.update_forward_refs()


class ProjectNodeTreeDto(CamelModel):
    roots: List[ProjectNodeTreeTypeNodeDto]
