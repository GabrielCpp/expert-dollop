from dataclasses import dataclass
from uuid import UUID


@dataclass
class ProjectDefinitionFunction:
    id: UUID
    name: str
    code: str
    ast: dict
    signature: list
    dependencies: dict
    struct_id: UUID
    package_id: UUID
