from expert_dollup.shared.modeling import CamelModel
from uuid import UUID
from typing import Optional, List
from datetime import datetime


class ProjectDefinitionContainerDto(CamelModel):
    id: UUID
    project_def_id: UUID
    name: str
    is_collection: bool
    instanciate_by_default: bool
    order_index: int
    config: dict
    value_type: str
    default_value: Optional[dict]
    path: List[UUID]


class ProjectDefinitionContainerPageDto(CamelModel):
    next_page_token: str
    limit: int
    results: List[ProjectDefinitionContainerDto]
