from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter


@dataclass
class ProjectDefinition:
    id: UUID
    name: str
    default_datasheet_id: UUID
    datasheet_def_id: UUID
    creation_date_utc: datetime


class ProjectDefinitionFilter(QueryFilter):
    id: Optional[UUID]
    name: Optional[str]
    default_datasheet_id: Optional[UUID]
    datasheet_def_id: Optional[UUID]
    creation_date_utc: Optional[datetime]
