from uuid import UUID
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter


@dataclass
class Datasheet:
    id: UUID
    name: str
    is_staged: bool
    datasheet_def_id: UUID
    from_datasheet_id: UUID
    creation_date_utc: datetime


class DatasheetFilter(QueryFilter):
    id: Optional[UUID]
    name: Optional[str]
    is_staged: Optional[bool]
    datasheet_def_id: Optional[UUID]
    from_datasheet_id: Optional[UUID]
    creation_date_utc: Optional[datetime]
