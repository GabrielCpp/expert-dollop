from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime
from expert_dollup.shared.starlette_injection import CamelModel
from pydantic import Field
from ..definition.aggregate_collection_dto import AggregateAttributeSchemaDto
from ..definition.aggregate_dto import AggregateAttributeDto


class NewDatasheetDto(CamelModel):
    name: str
    from_abstract_collection: UUID


class CloningDatasheetDto(CamelModel):
    clone_name: str
    target_datasheet_id: UUID


class DatasheetDto(CamelModel):
    id: UUID
    name: str
    project_definition_id: UUID
    from_abstract_collection: UUID
    from_datasheet_id: UUID
    attributes_schema: List[AggregateAttributeSchemaDto]
    default_instances: List[AggregateAttributeDto]
    creation_date_utc: datetime


class DatasheetImportDto(CamelModel):
    id: UUID
    name: str
    project_definition_id: UUID
