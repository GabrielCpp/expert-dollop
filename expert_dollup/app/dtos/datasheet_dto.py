from uuid import UUID
from dataclasses import dataclass
from datetime import datetime
from expert_dollup.shared.modeling import CamelModel


class DatasheetDto(CamelModel):
    id: UUID
    name: str
    is_staged: bool
    datasheet_def_id: UUID
    from_datasheet_id: UUID
    creation_date_utc: datetime
