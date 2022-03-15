from uuid import UUID
from typing import Optional, List, Union, Dict
from expert_dollup.shared.starlette_injection import CamelModel
from datetime import datetime
from expert_dollup.core.domains import (
    IntFieldConfig,
    DecimalFieldConfig,
    StringFieldConfig,
    BoolFieldConfig,
    StaticChoiceFieldConfig,
    CollapsibleContainerFieldConfig,
    StaticNumberFieldConfig,
)
from .dynamic_primitive import (
    IntFieldValueDto,
    DecimalFieldValueDto,
    StringFieldValueDto,
    BoolFieldValueDto,
    ReferenceIdDto,
    JsonSchemaDto,
    PrimitiveWithNoneUnionDto,
)


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
    StaticNumberFieldConfigDto,
    DecimalFieldConfigDto,
    StaticChoiceFieldConfigDto,
    StringFieldConfigDto,
    IntFieldConfigDto,
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
    value_validator: Optional[JsonSchemaDto]


value_type_lookup_map = {
    IntFieldValueDto: "IntFieldValue",
    DecimalFieldValueDto: "DecimalFieldValue",
    StringFieldValueDto: "StringFieldValue",
    BoolFieldValueDto: "BoolFieldValue",
    ReferenceIdDto: "ReferenceId",
    type(None): "null",
}


class ProjectDefinitionNodeDto(CamelModel):
    id: UUID
    project_definition_id: UUID
    name: str
    is_collection: bool
    instanciate_by_default: bool
    order_index: int
    config: NodeConfigDto
    default_value: PrimitiveWithNoneUnionDto
    path: List[UUID]
    creation_date_utc: datetime


class ProjectDefinitionNodePageDto(CamelModel):
    next_page_token: str
    limit: int
    results: List[ProjectDefinitionNodeDto]


class FieldUpdateInputDto(CamelModel):
    node_id: UUID
    value: PrimitiveWithNoneUnionDto
