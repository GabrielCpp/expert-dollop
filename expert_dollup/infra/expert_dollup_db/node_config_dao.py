from typing import List, Dict, Union, Optional
from typing_extensions import TypeAlias
from uuid import UUID
from pydantic import BaseModel
from decimal import Decimal


class IntFieldConfigDao(BaseModel):
    unit: str
    integer: int


class DecimalFieldConfigDao(BaseModel):
    unit: str
    precision: int
    numeric: Decimal


class StringFieldConfigDao(BaseModel):
    transforms: List[str]
    text: str


class BoolFieldConfigDao(BaseModel):
    enabled: bool


class AggregateReferenceConfigDao(BaseModel):
    from_collection: str


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
    selected: str


class CollapsibleContainerFieldConfigDao(BaseModel):
    is_collapsible: bool


FieldDetailsUnionDao: TypeAlias = Union[
    StaticNumberFieldConfigDao,
    DecimalFieldConfigDao,
    IntFieldConfigDao,
    StringFieldConfigDao,
    StaticChoiceFieldConfigDao,
    CollapsibleContainerFieldConfigDao,
    BoolFieldConfigDao,
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
