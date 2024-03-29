from uuid import UUID
from expert_dollup.shared.starlette_injection import CamelModel
from typing import Dict, Union
from typing_extensions import TypeAlias
from .dynamic_primitive import (
    IntFieldValueDto,
    DecimalFieldValueDto,
    StringFieldValueDto,
    BoolFieldValueDto,
    ReferenceIdDto,
)


LabelAttributeValueDto: TypeAlias = Union[
    BoolFieldValueDto,
    IntFieldValueDto,
    StringFieldValueDto,
    DecimalFieldValueDto,
    ReferenceIdDto,
]


class LabelDto(CamelModel):
    id: UUID
    label_collection_id: UUID
    order_index: int
    name: str
    attributes: Dict[str, LabelAttributeValueDto]
