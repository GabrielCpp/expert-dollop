from uuid import UUID
from dataclasses import dataclass, field
from typing import Dict
from .project_definition_node import ValueUnion


@dataclass
class LabelCollection:
    id: UUID
    datasheet_definition_id: UUID
    name: str
    default_properties: Dict[str, ValueUnion] = field(default_factory=dict)
