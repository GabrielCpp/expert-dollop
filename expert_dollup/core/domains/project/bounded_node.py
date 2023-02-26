from dataclasses import dataclass
from typing import List
from .project_node import ProjectNode
from ..definition.formula import Unit
from ..definition.project_definition_node import ProjectDefinitionNode


@dataclass
class BoundedNode:
    node: ProjectNode
    definition: ProjectDefinitionNode


@dataclass
class BoundedNodeSlice:
    bounded_nodes: List[BoundedNode]
