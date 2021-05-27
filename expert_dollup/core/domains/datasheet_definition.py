from uuid import UUID
from typing import Dict, Optional
from dataclasses import dataclass
from .project_definition_node import JsonSchema


@dataclass
class ElementPropertySchema:
    value_validator: JsonSchema


@dataclass
class DatasheetDefinition:
    id: UUID
    name: str
    properties: Dict[str, ElementPropertySchema]
