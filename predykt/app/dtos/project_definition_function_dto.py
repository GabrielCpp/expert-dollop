from predykt.shared.modeling import CamelModel
from uuid import UUID


class ProjectDefinitionFunctionDto(CamelModel):
    id: UUID
    name: str
    code: str
    ast: dict
    signature: list
    dependencies: dict
    struct_id: UUID
    package_id: UUID
