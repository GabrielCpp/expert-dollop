from dataclasses import dataclass
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter


@dataclass
class ProjectDefinition:
    id: UUID
    name: str
    revision: str
    creation_date_utc: datetime


class ProjectDefinitionFilter(QueryFilter):
    id: Optional[UUID]
    name: Optional[str]
    creation_date_utc: Optional[datetime]
