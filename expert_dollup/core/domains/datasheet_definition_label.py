from uuid import UUID
from dataclasses import dataclass


@dataclass
class Label:
    id: UUID
    label_collection_id: UUID
    order_index: int