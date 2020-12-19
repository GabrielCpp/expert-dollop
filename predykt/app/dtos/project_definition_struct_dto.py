from pydantic import BaseModel
from uuid import UUID


class ProjectDefinitionStructDto(BaseModel):
    id: UUID
    name: str
    package_id: UUID
    properties: dict
    dependencies: dict
