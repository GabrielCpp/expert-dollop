from dataclasses import dataclass, field
from uuid import UUID
from typing import Optional, List, Union, Dict
from typing_extensions import TypeAlias
from datetime import datetime
from enum import Enum
from expert_dollup.shared.database_services import QueryFilter
from decimal import Decimal

JsonSchema = dict


@dataclass
class IntFieldConfig:
    unit: Optional[str]
    default_value: int


@dataclass
class DecimalFieldConfig:
    unit: Optional[str]
    precision: int
    default_value: Decimal


@dataclass
class StringFieldConfig:
    transforms: List[str]
    default_value: str


@dataclass
class BoolFieldConfig:
    default_value: bool


@dataclass
class StaticNumberFieldConfig:
    pass_to_translation: bool
    precision: int
    unit: str

    @property
    def default_value(self):
        return None


@dataclass
class StaticChoiceOption:
    id: str
    label: str
    help_text: str


@dataclass
class StaticChoiceFieldConfig:
    options: List[StaticChoiceOption]
    default_value: str


@dataclass
class CollapsibleContainerFieldConfig:
    is_collapsible: bool

    @property
    def default_value(self):
        return None


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


FieldDetailsUnion: TypeAlias = Union[
    IntFieldConfig,
    StaticChoiceFieldConfig,
    DecimalFieldConfig,
    StringFieldConfig,
    BoolFieldConfig,
    CollapsibleContainerFieldConfig,
    StaticNumberFieldConfig,
    None,
]


@dataclass
class NodeMetaConfig:
    is_visible: bool = True


@dataclass
class ProjectDefinitionNode:
    id: UUID
    project_definition_id: UUID
    name: str
    is_collection: bool
    instanciate_by_default: bool
    order_index: int
    path: List[UUID]
    creation_date_utc: datetime
    translations: TranslationConfig
    field_details: Optional[FieldDetailsUnion] = None
    triggers: List[Trigger] = field(default_factory=list)
    meta: NodeMetaConfig = field(default_factory=lambda: NodeMetaConfig())

    @property
    def subpath(self):
        return [*self.path, self.id]

    @property
    def default_value(self):
        if self.field_details is None:
            return None

        return self.field_details.default_value


class ProjectDefinitionNodeFilter(QueryFilter):
    id: Optional[UUID]
    project_definition_id: Optional[UUID]
    name: Optional[str]
    is_collection: Optional[bool]
    instanciate_by_default: Optional[bool]
    order_index: Optional[int]
    path: Optional[List[UUID]]
    creation_date_utc: Optional[datetime]
    display_query_internal_id: Optional[UUID]


class FieldFormulaNodeFilter(QueryFilter):
    project_definition_id: Optional[UUID]
    name: str


class ProjectDefinitionNodePluckFilter(QueryFilter):
    names: List[str]
