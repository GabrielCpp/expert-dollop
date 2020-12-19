from pydantic import BaseModel
from uuid import UUID


class ProjectDefinitionPackageDto(BaseModel):
    id: UUID
    project_def_id: UUID
    name: str
    package: str
