from dataclasses import dataclass
from typing import List, Optional, Dict
from uuid import UUID
from .project_container import ProjectContainer
from .project_definition_node import ProjectDefinitionNode
from .project_container_meta import ProjectContainerMetaState


@dataclass
class ProjectContainerTreeTypeNode:
    definition: ProjectDefinitionNode
    state: ProjectContainerMetaState
    nodes: List["ProjectContainerTreeNode"]


@dataclass
class ProjectContainerTreeNode:
    node: ProjectContainer
    children: List[ProjectContainerTreeTypeNode]


@dataclass
class ProjectContainerTree:
    roots: List[ProjectContainerTreeTypeNode]
