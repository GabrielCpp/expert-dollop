from uuid import UUID
from expert_dollup.shared.modeling import CamelModel
from typing import Dict, Union
from .dynamic_primitive import (
    IntFieldValueDto,
    DecimalFieldValueDto,
    StringFieldValueDto,
    BoolFieldValueDto,
    ReferenceIdDto,
)


LabelAttributeValueDto = Union[
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
    attributes: Dict[str, LabelAttributeValueDto]
