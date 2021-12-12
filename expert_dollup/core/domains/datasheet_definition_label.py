from uuid import UUID
from dataclasses import dataclass, field
from typing import Dict
from .project_definition_node import ValueUnion


@dataclass
class Label:
    id: UUID
    label_collection_id: UUID
    order_index: int
    properties: Dict[str, ValueUnion] = field(default_factory=dict)
    aggregates: Dict[str, UUID] = field(default_factory=dict)
