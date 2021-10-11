from uuid import UUID
from typing import Optional, List, Union, Dict
from expert_dollup.shared.modeling import CamelModel
from expert_dollup.core.domains import *


class IntFieldConfigDto(CamelModel):
    unit: str


class DecimalFieldConfigDto(CamelModel):
    unit: str
    precision: int


class StringFieldConfigDto(CamelModel):
    transforms: List[str]


class BoolFieldConfigDto(CamelModel):
    is_checkbox: bool


class StaticChoiceOptionDto(CamelModel):
    id: str
    label: str
    help_text: str


class StaticChoiceFieldConfigDto(CamelModel):
    options: List[StaticChoiceOptionDto]


class StaticNumberFieldConfigDto(CamelModel):
    pass_to_translation: bool
    precision: int
    unit: str


class CollapsibleContainerFieldConfigDto(CamelModel):
    is_collapsible: bool


FieldDetailsUnionDto = Union[
    BoolFieldConfigDto,
    CollapsibleContainerFieldConfigDto,
    DecimalFieldConfigDto,
    StaticChoiceFieldConfigDto,
    StringFieldConfigDto,
    IntFieldConfigDto,
    StaticNumberFieldConfigDto,
    None,
]


config_type_lookup_map = {
    IntFieldConfigDto: "IntFieldConfig",
    DecimalFieldConfigDto: "DecimalFieldConfig",
    StringFieldConfigDto: "StringFieldConfig",
    BoolFieldConfigDto: "BoolFieldConfig",
    StaticChoiceFieldConfigDto: "StaticChoiceFieldConfig",
    CollapsibleContainerFieldConfigDto: "CollapsibleContainerFieldConfig",
    StaticNumberFieldConfigDto: "StaticNumberFieldConfig",
    type(None): "null",
}

assert len(FieldDetailsUnionDto.__args__) == len(config_type_lookup_map)

field_details_to_domain_map = {
    IntFieldConfigDto: IntFieldConfig,
    DecimalFieldConfigDto: DecimalFieldConfig,
    StringFieldConfigDto: StringFieldConfig,
    BoolFieldConfigDto: BoolFieldConfig,
    StaticChoiceFieldConfigDto: StaticChoiceFieldConfig,
    CollapsibleContainerFieldConfigDto: CollapsibleContainerFieldConfig,
    StaticNumberFieldConfigDto: StaticNumberFieldConfig,
    type(None): type(None),
}

field_details_from_domain = {v: k for k, v in field_details_to_domain_map.items()}

assert len(FieldDetailsUnionDto.__args__) == len(field_details_to_domain_map)


class TranslationConfigDto(CamelModel):
    help_text_name: str
    label: str


class TriggerDto(CamelModel):
    action: str
    target_type_id: UUID
    params: Dict[str, str]


class NodeMetaConfigDto(CamelModel):
    is_visible: bool


class NodeConfigDto(CamelModel):
    translations: TranslationConfigDto
    meta: NodeMetaConfigDto
    triggers: List[TriggerDto]
    field_details: Optional[FieldDetailsUnionDto]
    value_validator: Optional[JsonSchema]


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

value_type_lookup_map = {
    IntFieldValueDto: "IntFieldValue",
    DecimalFieldValueDto: "DecimalFieldValue",
    StringFieldValueDto: "StringFieldValue",
    BoolFieldValueDto: "BoolFieldValue",
    type(None): "null",
}


class ProjectDefinitionNodeDto(CamelModel):
    id: UUID
    project_def_id: UUID
    name: str
    is_collection: bool
    instanciate_by_default: bool
    order_index: int
    config: NodeConfigDto
    default_value: ValueUnionDto
    path: List[UUID]


class ProjectDefinitionNodePageDto(CamelModel):
    next_page_token: str
    limit: int
    results: List[ProjectDefinitionNodeDto]


class FieldUpdateInputDto(CamelModel):
    node_id: str
    value: ValueUnionDto
