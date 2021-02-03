from expert_dollup.shared.modeling import CamelModel
from typing import List
from uuid import UUID
from .project_container_dto import ProjectContainerDto
from .project_definition_container_dto import ProjectDefinitionContainerDto
from .project_container_meta_dto import ProjectContainerMetaDto


class ProjectContainerNodeDto(CamelModel):
    container: ProjectContainerDto
    definition: ProjectDefinitionContainerDto
    meta: ProjectContainerMetaDto
    children: List["ProjectContainerNodeDto"]


ProjectContainerNodeDto.update_forward_refs()


class ProjectContainerTreeDto(CamelModel):
    roots: List[ProjectContainerNodeDto]
