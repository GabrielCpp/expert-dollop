from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from typing import List
from .project_container import ProjectContainer
from .project_container_meta import ProjectContainerMeta
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
    nodes: List[ProjectContainer]
    metas: List[ProjectContainerMeta]
