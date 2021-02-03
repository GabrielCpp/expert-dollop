from expert_dollup.shared.modeling import CamelModel
from uuid import UUID


class ProjectContainerMetaDto(CamelModel):
    project_id: UUID
    type_id: UUID
    state: dict
