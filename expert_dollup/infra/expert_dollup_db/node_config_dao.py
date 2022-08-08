from typing import List, Dict, Union, Optional
from typing_extensions import TypeAlias
from uuid import UUID
from pydantic import BaseModel


JsonSchemaDao = dict


class IntFieldConfigDao(BaseModel):
    unit: str


class DecimalFieldConfigDao(BaseModel):
    unit: str
    precision: int


class StringFieldConfigDao(BaseModel):
    transforms: List[str]


class BoolFieldConfigDao(BaseModel):
    is_checkbox: bool


class StaticNumberFieldConfigDao(BaseModel):
    pass_to_translation: bool
    precision: int
    unit: str


class StaticChoiceOptionDao(BaseModel):
    id: str
    label: str
    help_text: str


class StaticChoiceFieldConfigDao(BaseModel):
    options: List[StaticChoiceOptionDao]


class CollapsibleContainerFieldConfigDao(BaseModel):
    is_collapsible: bool


FieldDetailsUnionDao: TypeAlias = Union[
    StaticNumberFieldConfigDao,
    DecimalFieldConfigDao,
    IntFieldConfigDao,
    StringFieldConfigDao,
    BoolFieldConfigDao,
    StaticChoiceFieldConfigDao,
    CollapsibleContainerFieldConfigDao,
    None,
]


class NodeMetaConfigDao(BaseModel):
    is_visible: bool


class TriggerDao(BaseModel):
    action: str
    target_type_id: UUID
    params: Dict[str, str]


class TranslationConfigDao(BaseModel):
    help_text_name: str
    label: str


class NodeConfigDao(BaseModel):
    translations: TranslationConfigDao
    triggers: List[TriggerDao]
    meta: NodeMetaConfigDao
    field_details: Optional[FieldDetailsUnionDao]
    value_validator: Optional[JsonSchemaDao]
