from uuid import UUID
from expert_dollup.shared.modeling import CamelModel
from pydantic import StrictBool, StrictInt, StrictStr, StrictFloat
from typing import Dict, Union

StrictValueUnionDto = Union[StrictBool, StrictInt, StrictStr, StrictFloat, None]


class LabelDto(CamelModel):
    id: UUID
    label_collection_id: UUID
    order_index: int
    properties: Dict[str, StrictValueUnionDto]
    aggregates: Dict[str, UUID]
