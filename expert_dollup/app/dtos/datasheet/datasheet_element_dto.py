from uuid import UUID
from typing import Dict, Optional, List
from datetime import datetime
from expert_dollup.shared.starlette_injection import CamelModel
from ..dynamic_primitive import PrimitiveUnionDto


class AttributeDto(CamelModel):
    name: str
    value: PrimitiveWithReferenceUnionDto


class DatasheetElementDto(CamelModel):
    id: UUID
    datasheet_id: UUID
    aggregate_id: UUID
    ordinal: int
    attributes: List[AttributeDto]
    original_datasheet_id: UUID
    original_owner_organization_id: UUID
    creation_date_utc: datetime


class NewDatasheetElementDto(CamelModel):
    aggregate_id: UUID
    attributes: List[AttributeDto]


class DatasheetElementUpdateDto(CamelModel):
    id: UUID
    aggregate_id: UUID
    attributes: List[AttributeDto]


class DatasheetElementImportDto(CamelModel):
    datasheet_id: UUID
    element_def_id: UUID
    child_element_reference: UUID
    attributes: Dict[str, PrimitiveUnionDto]
    original_datasheet_id: UUID
    original_owner_organization_id: UUID
    creation_date_utc: datetime
