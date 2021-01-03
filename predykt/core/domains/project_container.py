from dataclasses import dataclass
from typing import List
from uuid import UUID


@dataclass
class ProjectContainer:
    id: UUID
    project_id: UUID
    type_id: UUID
    path: List[UUID]
    value: dict
