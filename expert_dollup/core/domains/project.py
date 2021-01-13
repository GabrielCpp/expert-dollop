from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class Project:
    id: UUID
    name: str
    is_staged: bool
    project_def_id: UUID
    datasheet_id: UUID
