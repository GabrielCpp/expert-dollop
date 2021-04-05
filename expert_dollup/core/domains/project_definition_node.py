from dataclasses import dataclass
from uuid import UUID
from enum import Enum
from typing import Optional, List, Union
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter

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


FieldDetailsUnion = Union[
    IntFieldConfig,
    DecimalFieldConfig,
    StringFieldConfig,
    BoolFieldConfig,
    StaticChoiceFieldConfig,
    CollapsibleContainerFieldConfig,
    None,
]


@dataclass
class NodeConfig:
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
    config: Optional[NodeConfig]
    default_value: ValueUnion
    path: Optional[List[UUID]]
    creation_date_utc: Optional[datetime]
