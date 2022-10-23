from uuid import UUID, uuid4
from typing import Optional, List
from datetime import datetime
from expert_dollup.shared.starlette_injection import CamelModel
from pydantic import Field
from ..definition.aggregate_dto import AggregateAttributeDto
from ..definition.aggregate_collection_dto import AggregateAttributeSchemaDto


class NewDatasheetDto(CamelModel):
    name: str
    abstract_collection_id: UUID


class CloningDatasheetDto(CamelModel):
    clone_name: str
    target_datasheet_id: UUID


class InstanceAttributeSchemaDto(CamelModel):
    name: str
    is_readonly: bool


class InstanceSchemaDto(CamelModel):
    id: UUID
    is_extendable: bool
    attributes_schema: List[InstanceAttributeSchemaDto]


class DatasheetDto(CamelModel):
    id: UUID
    name: str
    project_definition_id: UUID
    abstract_collection_id: UUID
    from_datasheet_id: UUID
    attributes_schema: List[AggregateAttributeSchemaDto]
    instances_schema: List[InstanceSchemaDto]
    creation_date_utc: datetime


class DatasheetImportDto(CamelModel):
    id: UUID
    name: str
    project_definition_id: UUID
