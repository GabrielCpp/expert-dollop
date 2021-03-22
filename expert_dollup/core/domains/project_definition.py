from dataclasses import dataclass
from typing import List
from uuid import UUID
from datetime import datetime


@dataclass
class ProjectDefinition:
    id: UUID
    name: str
    default_datasheet_id: UUID
    datasheet_def_id: UUID
    creation_date_utc: datetime
