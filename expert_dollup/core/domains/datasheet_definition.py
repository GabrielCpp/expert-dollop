from uuid import UUID
from typing import Dict
from dataclasses import dataclass


@dataclass
class DatasheetDefinition:
    id: UUID
    name: str
    element_properties_schema: Dict[str, dict]
