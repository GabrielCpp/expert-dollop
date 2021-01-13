from dataclasses import dataclass
from uuid import UUID


@dataclass
class ProjectDefinitionStruct:
    id: UUID
    name: str
    package_id: UUID
    properties: dict
    dependencies: dict
