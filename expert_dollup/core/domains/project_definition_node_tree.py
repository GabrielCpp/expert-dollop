from dataclasses import dataclass
from uuid import UUID
from typing import Optional, List
from datetime import datetime
from .project_definition_node import ProjectDefinitionNode


@dataclass
class ProjectDefinitionTreeNode:
    definition: ProjectDefinitionNode
    children: List["ProjectDefinitionTreeNode"]


@dataclass
class ProjectDefinitionNodeTree:
    roots: List[ProjectDefinitionTreeNode]
