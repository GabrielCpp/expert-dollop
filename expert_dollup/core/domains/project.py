from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from typing import List
from .project_node import ProjectNode
from .project_node_meta import ProjectNodeMeta
from .ressource import Ressource


@dataclass
class ProjectDetails:
    id: UUID
    name: str
    is_staged: bool
    project_def_id: UUID
    datasheet_id: UUID


@dataclass
class Project:
    ressource: Ressource
    details: ProjectDetails
    nodes: List[ProjectNode]
    metas: List[ProjectNodeMeta]
