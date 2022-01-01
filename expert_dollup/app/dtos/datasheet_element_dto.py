from uuid import UUID
from typing import Dict, Optional, List
from datetime import datetime
from expert_dollup.shared.starlette_injection import CamelModel
from .dynamic_primitive import PrimitiveUnionDto


class DatasheetElementDto(CamelModel):
    datasheet_id: UUID
    element_def_id: UUID
    child_element_reference: UUID
    properties: Dict[str, PrimitiveUnionDto]
    original_datasheet_id: UUID
    creation_date_utc: datetime


class DatasheetElementImportDto(CamelModel):
    datasheet_id: UUID
    element_def_id: UUID
    child_element_reference: UUID
    properties: Dict[str, PrimitiveUnionDto]
    original_datasheet_id: UUID


class DatasheetElementPageDto(CamelModel):
    next_page_token: Optional[str]
    limit: int
    results: List[DatasheetElementDto]
