from uuid import UUID
from typing import List, Dict
from datetime import datetime
from expert_dollup.shared.starlette_injection import CamelModel
from .dynamic_primitive import PrimitiveUnionDto


class DatasheetDefinitionElementPropertyDto(CamelModel):
    is_readonly: bool
    value: PrimitiveUnionDto


class DatasheetDefinitionElementDto(CamelModel):
    id: UUID
    unit_id: str
    is_collection: bool
    datasheet_def_id: UUID
    order_index: int
    name: str
    tags: List[UUID]
    default_properties: Dict[str, DatasheetDefinitionElementPropertyDto]
    creation_date_utc: datetime
