from uuid import UUID
from enum import Enum
from typing import Optional, List, Union
from datetime import datetime
from expert_dollup.shared.modeling import CamelModel, BaseModel


class IntFieldConfigDto(CamelModel):
    validator: dict


class DecimalFieldConfigDto(CamelModel):
    validator: dict
    precision: int


class StringFieldConfigDto(CamelModel):
    validator: dict
    transforms: List[str]


class BoolFieldConfigDto(CamelModel):
    is_checkbox: bool


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
    BoolFieldConfigDto,
    CollapsibleContainerFieldConfigDto,
    DecimalFieldConfigDto,
    StaticChoiceFieldConfigDto,
    StringFieldConfigDto,
    IntFieldConfigDto,
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
