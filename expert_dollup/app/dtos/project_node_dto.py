from expert_dollup.shared.starlette_injection import CamelModel
from typing import List, Optional, Union
from uuid import UUID
from .dynamic_primitive import PrimitiveWithNoneUnionDto


class ProjectNodeDto(CamelModel):
    id: UUID
    project_id: UUID
    type_id: UUID
    type_name: str
    path: List[UUID]
    type_path: List[UUID]
    value: PrimitiveWithNoneUnionDto
    label: str = ""


class ProjectNodeCollectionTargetDto(CamelModel):
    parent_node_id: Optional[UUID]
    collection_type_id: UUID
