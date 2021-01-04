from predykt.shared.modeling import CamelModel
from uuid import UUID


class ProjectDefinitionStructDto(CamelModel):
    id: UUID
    name: str
    package_id: UUID
    properties: dict
    dependencies: dict
