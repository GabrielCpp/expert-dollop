from dataclasses import dataclass
from typing import List
from .project_node import ProjectNode
from .project_definition import ProjectDefinition
from .formula import FormulaInstance


@dataclass
class BoundedNode:
    node: ProjectNode
    definition: ProjectDefinition


@dataclass
class BoundedNodeSlice:
    bounded_nodes: List[BoundedNode]
    formulas_result: List[FormulaInstance]
