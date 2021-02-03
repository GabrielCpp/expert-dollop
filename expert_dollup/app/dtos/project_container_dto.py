from expert_dollup.shared.modeling import CamelModel
from typing import List
from uuid import UUID


class ProjectContainerDto(CamelModel):
    id: UUID
    project_id: UUID
    type_id: UUID
    path: List[UUID]
    value: dict
