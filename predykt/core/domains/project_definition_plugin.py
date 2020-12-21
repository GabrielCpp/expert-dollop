from dataclasses import dataclass
from uuid import UUID


@dataclass
class ProjectDefinitionPlugin:
    id: UUID
    validation_schema: dict
    default_config: dict
    form_config: dict
    name: str
