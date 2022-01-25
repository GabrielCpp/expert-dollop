from dataclasses import dataclass
from typing import List
from .project_node import ProjectNode
from .project_definition_node import ProjectDefinitionNode
from .formula import UnitInstance


@dataclass
class BoundedNode:
    node: ProjectNode
    definition: ProjectDefinitionNode


@dataclass
class BoundedNodeSlice:
    bounded_nodes: List[BoundedNode]
    unit_instances: List[UnitInstance]
