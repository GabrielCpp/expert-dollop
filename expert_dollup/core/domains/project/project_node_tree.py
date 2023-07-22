from dataclasses import dataclass
from typing import List
from .project_node import ProjectNode
from .project_node_meta import ProjectNodeMetaState
from ..definition.project_definition_node import ProjectDefinitionNode


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
