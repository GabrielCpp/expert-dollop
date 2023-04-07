from dataclasses import dataclass
from uuid import UUID
from typing import List
from datetime import datetime


@dataclass
class Tag:
    name: str
    version: str


@dataclass
class ChangeSet:
    nodes: List[ProjectNode]
    metas: List[ProjectNodeMeta]
    collection: List[AggregateCollection]
    aggregates: List[Aggregate]


@dataclass
class Commit:
    ressource_id: UUID
    version: str
    changes: ChangeSet
    creation_date_utc: datetime
