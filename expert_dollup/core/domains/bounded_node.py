from dataclasses import dataclass
from .project_node import ProjectNode
from .project_definition import ProjectDefinition


@dataclass
class BoundedNode:
    node: ProjectNode
    definition: ProjectDefinition
