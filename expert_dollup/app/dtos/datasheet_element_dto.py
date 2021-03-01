from uuid import UUID
from datetime import datetime
from expert_dollup.shared.modeling import CamelModel


class DatasheetElementDto(CamelModel):
    datasheet_id: UUID
    element_def_id: UUID
    child_element_reference: UUID
    properties: dict
    original_datasheet_id: UUID
    creation_date_utc: datetime