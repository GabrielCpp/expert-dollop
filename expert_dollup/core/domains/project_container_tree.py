from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID
from .project_container import ProjectContainer
from .project_definition_node import ProjectDefinitionNode
from .project_container_meta import ProjectContainerMetaState


@dataclass
class ProjectContainerTypeGroup:
    children: List["ProjectContainerTreeNode"]


@dataclass
class ProjectContainerTreeNode:
    container: ProjectContainer
    definition: ProjectDefinitionNode
    state: ProjectContainerMetaState
    types: List[ProjectContainerTypeGroup]


@dataclass
class ProjectContainerTree:
    roots: List[ProjectContainerTreeNode]
