from dataclasses import dataclass, field
from uuid import UUID
from typing import Optional, List, Union, Dict
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter
from enum import Enum

JsonSchema = dict


@dataclass
class IntFieldConfig:
    unit: str


@dataclass
class DecimalFieldConfig:
    unit: str
    precision: int


@dataclass
class StringFieldConfig:
    transforms: List[str]


@dataclass
class BoolFieldConfig:
    is_checkbox: bool


@dataclass
class StaticNumberFieldConfig:
    pass_to_translation: bool
    precision: int
    unit: str


@dataclass
class StaticChoiceOption:
    id: str
    label: str
    help_text: str


@dataclass
class StaticChoiceFieldConfig:
    options: List[StaticChoiceOption]


@dataclass
class CollapsibleContainerFieldConfig:
    is_collapsible: bool


@dataclass
class StaticNumberFieldConfig:
    pass_to_translation: bool
    precision: int
    unit: str


class TriggerAction(Enum):
    CHANGE_NAME = "CHANGE_NAME"
    SET_VISIBILITY = "SET_VISIBILITY"


@dataclass
class Trigger:
    action: TriggerAction
    target_type_id: UUID
    params: Dict[str, str]


@dataclass
class TranslationConfig:
    help_text_name: str
    label: str


FieldDetailsUnion = Union[
    IntFieldConfig,
    DecimalFieldConfig,
    StringFieldConfig,
    BoolFieldConfig,
    StaticChoiceFieldConfig,
    CollapsibleContainerFieldConfig,
    StaticNumberFieldConfig,
    None,
]


@dataclass
class NodeMetaConfig:
    is_visible: bool = True


@dataclass
class NodeConfig:
    translations: TranslationConfig
    triggers: List[Trigger] = field(default_factory=list)
    meta: NodeMetaConfig = field(default_factory=lambda: NodeMetaConfig())
    field_details: Optional[FieldDetailsUnion] = None
    value_validator: Optional[JsonSchema] = None


ValueUnion = Union[bool, int, str, float, None]


@dataclass
class ProjectDefinitionNode:
    id: UUID
    project_def_id: UUID
    name: str
    is_collection: bool
    instanciate_by_default: bool
    order_index: int
    config: NodeConfig
    default_value: ValueUnion
    path: List[UUID]
    creation_date_utc: datetime

    @property
    def subpath(self):
        return [*self.path, self.id]


class ProjectDefinitionNodeFilter(QueryFilter):
    id: Optional[UUID]
    project_def_id: Optional[UUID]
    name: Optional[str]
    is_collection: Optional[bool]
    instanciate_by_default: Optional[bool]
    order_index: Optional[int]
    default_value: ValueUnion
    path: Optional[List[UUID]]
    creation_date_utc: Optional[datetime]
    display_query_internal_id: Optional[UUID]


class ProjectDefinitionNodePluckFilter(QueryFilter):
    names: List[str]