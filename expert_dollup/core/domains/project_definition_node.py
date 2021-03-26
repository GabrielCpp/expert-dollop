from dataclasses import dataclass
from uuid import UUID
from typing import Optional, List, Union
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter


@dataclass
class IntFieldConfig:
    validator: dict


@dataclass
class DecimalFieldConfig:
    validator: dict
    precision: int


@dataclass
class StringFieldConfig:
    validator: dict
    transforms: List[str]


@dataclass
class BoolFieldConfig:
    validator: dict


@dataclass
class StaticChoiceOption:
    id: str
    label: str
    help_text: str


@dataclass
class StaticChoiceFieldConfig:
    validator: dict
    options: List[StaticChoiceOption]


@dataclass
class CollapsibleContainerFieldConfig:
    is_collapsible: bool


@dataclass
class NodeConfig:
    value_type: Union[
        IntFieldConfig,
        DecimalFieldConfig,
        StringFieldConfig,
        BoolFieldConfig,
        StaticChoiceFieldConfig,
        CollapsibleContainerFieldConfig,
        None,
    ] = None


@dataclass
class IntFieldValue:
    integer: int


@dataclass
class DecimalFieldValue:
    numeric: float


@dataclass
class StringFieldValue:
    text: str


@dataclass
class BoolFieldValue:
    enabled: bool


ValueUnion = Union[
    BoolFieldValue, StringFieldValue, IntFieldValue, DecimalFieldValue, None
]


@dataclass
class ProjectDefinitionNode:
    id: UUID
    project_def_id: UUID
    name: str
    is_collection: bool
    instanciate_by_default: bool
    order_index: int
    config: NodeConfig
    value_type: str
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
    value_type: Optional[str]
    default_value: ValueUnion
    path: Optional[List[UUID]]
    creation_date_utc: Optional[datetime]
