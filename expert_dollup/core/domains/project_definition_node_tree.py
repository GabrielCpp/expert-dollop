from dataclasses import dataclass
from uuid import UUID
from typing import Optional, List
from datetime import datetime
from .project_definition_node import ProjectDefinitionContainerNode


@dataclass
class ProjectDefinitionContainerNodeTreeNode:
    definition: ProjectDefinitionContainerNode
    children: List["ProjectDefinitionContainerNodeTreeNode"]


@dataclass
class ProjectDefinitionContainerNodeTree:
    roots: List[ProjectDefinitionContainerNodeTreeNode]
