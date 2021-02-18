from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID
from .project_container import ProjectContainer
from .project_definition_container import ProjectDefinitionContainer
from .project_container_meta import ProjectContainerMeta


@dataclass
class ProjectContainerNode:
    container: ProjectContainer
    definition: ProjectDefinitionContainer
    meta: Optional[ProjectContainerMeta]
    children: List["ProjectContainerNode"]


@dataclass
class ProjectContainerTree:
    roots: List[ProjectContainerNode]