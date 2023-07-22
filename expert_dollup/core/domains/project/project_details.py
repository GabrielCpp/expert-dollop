from dataclasses import dataclass
from uuid import UUID
from typing import List, Union, Optional
from datetime import datetime
from .project_node import ProjectNode
from .project_node_meta import ProjectNodeMeta
from ..ressource import Ressource


@dataclass
class DatasheetReference:
    abstract_collection_id: UUID
    name: str
    datasheet_id: Optional[UUID]


@dataclass
class ProjectDetails:
    id: UUID
    name: str
    project_definition_id: UUID
    datasheets: List[DatasheetReference]
    creation_date_utc: datetime


@dataclass
class Project:
    ressource: Ressource
    details: ProjectDetails
    nodes: List[ProjectNode]
    metas: List[ProjectNodeMeta]
