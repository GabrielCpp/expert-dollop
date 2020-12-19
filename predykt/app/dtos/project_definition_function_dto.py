from pydantic import BaseModel
from uuid import UUID


class ProjectDefinitionFunctionDto(BaseModel):
    id: UUID
    name: str
    code: str
    ast: dict
    signature: list
    dependencies: dict
    struct_id: UUID
    package_id: UUID
