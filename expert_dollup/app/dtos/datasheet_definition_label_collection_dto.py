from uuid import UUID
from expert_dollup.shared.starlette_injection import CamelModel
from typing import Dict, Union
from typing_extensions import TypeAlias
from .dynamic_primitive import JsonSchemaDto


class CollectionAggregateDto(CamelModel):
    from_collection: str


class DatasheetAggregateDto(CamelModel):
    from_datasheet: str


class FormulaAggregateDto(CamelModel):
    from_formula: str


class StaticPropertyDto(CamelModel):
    json_schema: JsonSchemaDto


LabelAttributeSchemaDtoUnion: TypeAlias = Union[
    StaticPropertyDto,
    CollectionAggregateDto,
    DatasheetAggregateDto,
    FormulaAggregateDto,
]


class LabelCollectionDto(CamelModel):
    id: UUID
    project_definition_id: UUID
    name: str
    attributes_schema: Dict[str, LabelAttributeSchemaDtoUnion]
