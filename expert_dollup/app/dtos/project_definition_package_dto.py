from expert_dollup.shared.modeling import CamelModel
from uuid import UUID


class ProjectDefinitionPackageDto(CamelModel):
    id: UUID
    project_def_id: UUID
    name: str
    package: str
