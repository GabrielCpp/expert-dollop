from uuid import UUID
from expert_dollup.shared.modeling import CamelModel
from typing import Dict, Union
from .project_definition_node_dto import JsonSchema


class CollectionAggregateDto(CamelModel):
    from_collection: str


class DatasheetAggregateDto(CamelModel):
    from_datasheet: str


class FormulaAggregateDto(CamelModel):
    from_formula: str


class StaticPropertyDto(CamelModel):
    json_schema: JsonSchema


LabelAttributeSchemaDtoUnion = Union[
    StaticPropertyDto,
    CollectionAggregateDto,
    DatasheetAggregateDto,
    FormulaAggregateDto,
]


class LabelCollectionDto(CamelModel):
    id: UUID
    datasheet_definition_id: UUID
    name: str
    attributes_schema: Dict[str, LabelAttributeSchemaDtoUnion]
