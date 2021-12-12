from uuid import UUID
from expert_dollup.shared.modeling import CamelModel
from pydantic import Field
from typing import Dict, Union
from .project_definition_node_dto import JsonSchema


class CollectionAggregateDto(CamelModel):
    from_collection: str


class DatasheetAggregateDto(CamelModel):
    from_datasheet: str


AcceptedAggregateDtoUnion = Union[CollectionAggregateDto, DatasheetAggregateDto]


class LabelCollectionDto(CamelModel):
    id: UUID
    datasheet_definition_id: UUID
    name: str
    properties_schema: Dict[str, JsonSchema]
    accepted_aggregates: Dict[str, AcceptedAggregateDtoUnion]
