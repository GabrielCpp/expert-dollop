from dataclasses import dataclass
from uuid import UUID


@dataclass
class ProjectContainerMeta:
    project_id: UUID
    type_id: UUID
    state: dict
