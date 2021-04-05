from expert_dollup.shared.modeling import CamelModel
from typing import List, Optional, Union
from uuid import UUID
from .project_definition_node_dto import ValueUnionDto


class ProjectContainerDto(CamelModel):
    id: UUID
    project_id: UUID
    type_id: UUID
    path: List[UUID]
    value: ValueUnionDto


class ProjectContainerPageDto(CamelModel):
    next_page_token: Optional[str]
    limit: int
    results: List[ProjectContainerDto]


class ProjectContainerCollectionTargetDto(CamelModel):
    parent_container_id: Optional[UUID]
    collection_type_id: UUID
