from uuid import UUID
from typing import List, Dict, Union
from datetime import datetime
from expert_dollup.shared.modeling import CamelModel


class DatasheetDefinitionElementPropertyDto(CamelModel):
    is_readonly: bool
    value: Union[float, str, bool]


class DatasheetDefinitionElementDto(CamelModel):
    id: UUID
    unit_id: str
    is_collection: bool
    datasheet_def_id: UUID
    order_index: int
    name: str
    tags: List[UUID]
    default_properties: Dict[str, DatasheetDefinitionElementPropertyDto]
