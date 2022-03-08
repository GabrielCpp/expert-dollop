from uuid import UUID
from dataclasses import dataclass, field
from typing import Dict, Union, Optional

from expert_dollup.shared.database_services import QueryFilter
from .project_definition_node import JsonSchema


@dataclass(frozen=True)
class CollectionAggregate:
    from_collection: str


@dataclass(frozen=True)
class DatasheetAggregate:
    from_datasheet: str


@dataclass(frozen=True)
class FormulaAggregate:
    from_formula: str


@dataclass(frozen=True)
class StaticProperty:
    json_schema: JsonSchema


LabelAttributeSchemaUnion = Union[
    StaticProperty, CollectionAggregate, DatasheetAggregate, FormulaAggregate
]


@dataclass
class LabelCollection:
    id: UUID
    project_definition_id: UUID
    name: str
    attributes_schema: Dict[str, LabelAttributeSchemaUnion] = field(
        default_factory=dict
    )


class LabelCollectionFilter(QueryFilter):
    id: Optional[UUID]
    project_definition_id: Optional[UUID]
    name: Optional[str]
