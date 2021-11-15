from uuid import UUID
from typing import Union, Dict, Optional, List
from datetime import datetime
from expert_dollup.shared.modeling import CamelModel


class DatasheetElementDto(CamelModel):
    datasheet_id: UUID
    element_def_id: UUID
    child_element_reference: UUID
    properties: Dict[str, Union[float, str, bool]]
    original_datasheet_id: UUID
    creation_date_utc: datetime


class DatasheetElementImportDto(CamelModel):
    datasheet_id: UUID
    element_def_id: UUID
    child_element_reference: UUID
    properties: Dict[str, Union[float, str, bool]]
    original_datasheet_id: UUID


class DatasheetElementPageDto(CamelModel):
    next_page_token: Optional[str]
    limit: int
    results: List[DatasheetElementDto]
