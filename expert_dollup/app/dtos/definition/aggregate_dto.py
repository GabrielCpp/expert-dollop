from uuid import UUID
from typing import List
from expert_dollup.shared.starlette_injection import CamelModel
from ..dynamic_primitive import PrimitiveWithReferenceUnionDto


class AggregateAttributeDto(CamelModel):
    name: str
    is_readonly: bool
    value: PrimitiveWithReferenceUnionDto


class AggregateDto(CamelModel):
    id: UUID
    collection_id: UUID
    ordinal: int
    name: str
    is_extendable: bool
    attributes: List[AggregateAttributeDto]


class NewAggregateDto(CamelModel):
    ordinal: int
    name: str
    is_extendable: bool
    attributes: List[AggregateAttributeDto]
