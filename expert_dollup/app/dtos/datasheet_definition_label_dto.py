from uuid import UUID
from dataclasses import dataclass
from expert_dollup.shared.modeling import CamelModel


class LabelDto(CamelModel):
    id: UUID
    label_collection_id: UUID
    order_index: int