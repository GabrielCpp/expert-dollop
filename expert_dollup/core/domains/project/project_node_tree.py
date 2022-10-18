from dataclasses import dataclass
from typing import List
from .project_node import ProjectNode
from .project_definition_node import ProjectDefinitionNode
from .project_node_meta import ProjectNodeMetaState


@dataclass
class ProjectNodeTreeTypeNode:
    definition: ProjectDefinitionNode
    state: ProjectNodeMetaState
    nodes: List["ProjectNodeTreeNode"]


@dataclass
class ProjectNodeTreeNode:
    node: ProjectNode
    children: List[ProjectNodeTreeTypeNode]


@dataclass
class ProjectNodeTree:
    roots: List[ProjectNodeTreeTypeNode]
