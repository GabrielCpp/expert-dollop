from expert_dollup.shared.modeling import CamelModel, BaseModel
from uuid import UUID
from typing import Optional, List, Union
from datetime import datetime


class IntFieldConfigDto(CamelModel):
    validator: dict


class DecimalFieldConfigDto(CamelModel):
    validator: dict
    precision: int


class StringFieldConfigDto(CamelModel):
    validator: dict
    transforms: List[str]


class BoolFieldConfigDto(CamelModel):
    validator: dict


class StaticChoiceOptionDto(CamelModel):
    id: str
    label: str
    help_text: str


class StaticChoiceFieldConfigDto(CamelModel):
    validator: dict
    options: List[StaticChoiceOptionDto]


class CollapsibleContainerFieldConfigDto(CamelModel):
    is_collapsible: bool


NodeConfigValueType = Union[
    IntFieldConfigDto,
    DecimalFieldConfigDto,
    StringFieldConfigDto,
    BoolFieldConfigDto,
    StaticChoiceFieldConfigDto,
    CollapsibleContainerFieldConfigDto,
    None,
]


class NodeConfigDto(CamelModel):
    value_type: NodeConfigValueType


class IntFieldValueDto(CamelModel):
    integer: int


class DecimalFieldValueDto(CamelModel):
    numeric: float


class StringFieldValueDto(CamelModel):
    text: str


class BoolFieldValueDto(CamelModel):
    enabled: bool


ValueUnionDto = Union[
    IntFieldValueDto,
    DecimalFieldValueDto,
    StringFieldValueDto,
    BoolFieldValueDto,
    None,
]


class ProjectDefinitionNodeDto(CamelModel):
    id: UUID
    project_def_id: UUID
    name: str
    is_collection: bool
    instanciate_by_default: bool
    order_index: int
    config: NodeConfigDto
    value_type: str
    default_value: ValueUnionDto
    path: List[UUID]


class ProjectDefinitionNodePageDto(CamelModel):
    next_page_token: str
    limit: int
    results: List[ProjectDefinitionNodeDto]
