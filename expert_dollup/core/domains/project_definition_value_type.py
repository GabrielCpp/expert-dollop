from dataclasses import dataclass
from uuid import UUID
from typing import Optional, List
from datetime import datetime


@dataclass
class ProjectDefinitionValueType:
    id: str
    value_json_schema: dict
    attributes_json_schema: dict
    display_name: str
