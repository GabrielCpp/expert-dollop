from dataclasses import dataclass
from uuid import UUID


@dataclass
class ProjectDefinitionPackage:
    id: UUID
    project_def_id: UUID
    name: str
    package: str
