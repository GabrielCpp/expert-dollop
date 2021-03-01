from uuid import UUID
from dataclasses import dataclass


@dataclass
class LabelCollection:
    id: UUID
    datasheet_definition_id: UUID
    name: str
