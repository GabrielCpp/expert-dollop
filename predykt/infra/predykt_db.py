from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects import postgresql
from sqlalchemy import Table, MetaData, String, Boolean, DateTime, Column, Binary, Text
from sqlalchemy_utils.types.uuid import UUIDType
from databases import Database
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional


class PredyktDatabase(Database):
    pass


metadata = MetaData()

project_definition_table = Table(
    'project_definition', metadata,
    Column('id', postgresql.UUID(), nullable=False, primary_key=True),
    Column('name', String, nullable=False),
    Column('default_datasheet_id', postgresql.UUID(), nullable=False),
    Column('owner_id', postgresql.UUID(), nullable=False),
    Column('creation_date_utc', DateTime(timezone=True), nullable=False),
)


class ProjectDefinitionDao(BaseModel):
    id: UUID
    name: str
    default_datasheet_id: UUID
    owner_id: UUID
    creation_date_utc: datetime


project_definition_container_table = Table(
    "project_definition_container",
    metadata,
    Column('id', UUIDType(), nullable=False, primary_key=True),
    Column('project_def_id', UUIDType(), nullable=False),
    Column('name', String, nullable=False),
    Column('is_collection', Boolean, nullable=False),
    Column('instanciate_by_default', Boolean, nullable=False),
    Column('custom_attributes', postgresql.JSON(), nullable=False),
    Column('value_type', String, nullable=False),
    Column('default_value', postgresql.JSON(), nullable=True),
    Column('path', ARRAY(String, dimensions=1), nullable=False),
    Column('mixed_paths', ARRAY(String, dimensions=1), nullable=False),
    Column('creation_date_utc', DateTime(timezone=True), nullable=False),
)


class ProjectDefinitionContainerDao(BaseModel):
    id: UUID
    project_def_id: UUID
    name: str
    is_collection: bool
    instanciate_by_default: bool
    custom_attributes: dict
    value_type: str
    default_value: Optional[dict]
    path: List[str]
    mixed_paths: List[str]
    creation_date_utc: datetime


project_definition_package_table = Table(
    'project_definition_package',
    metadata,
    Column('id', UUIDType(), nullable=False, primary_key=True),
    Column('project_def_id', UUIDType(), nullable=False),
    Column('name', String, nullable=False),
    Column('package', String, nullable=False)
)


class ProjectDefinitionPackageDao(BaseModel):
    id: UUID
    project_def_id: UUID
    name: str
    package: str


project_definition_struct_table = Table(
    "project_definition_struct",
    metadata,
    Column('id', UUIDType(), nullable=False, primary_key=True),
    Column('name', String, nullable=False),
    Column('package_id', String, nullable=False),
    Column('properties', postgresql.JSON(), nullable=True),
    Column('dependencies', postgresql.JSON(), nullable=True),
)


class ProjectDefinitionStructDao(BaseModel):
    id: UUID
    name: str
    package_id: UUID
    properties: dict
    dependencies: dict


project_definition_function_table = Table(
    "project_definition_function",
    metadata,
    Column('id', UUIDType(), nullable=False, primary_key=True),
    Column('name', String, nullable=False),
    Column('code', Text, nullable=False),
    Column('ast', postgresql.JSON(), nullable=True),
    Column('signature', postgresql.JSON(), nullable=True),
    Column('dependencies', postgresql.JSON(), nullable=True),
    Column('struct_id', UUIDType(), nullable=True),
    Column('package_id', UUIDType(), nullable=True)
)


class ProjectDefinitionFunctionDao(BaseModel):
    id: UUID
    name: str
    code: str
    ast: dict
    signature: list
    dependencies: dict
    struct_id: UUID
    package_id: UUID


project_table = Table(
    "project",
    metadata,
    Column('id', UUIDType(), nullable=False, primary_key=True),
    Column('name', String, nullable=False),
    Column('is_staged', Boolean, nullable=False),
    Column('project_def_id', UUIDType(), nullable=True),
    Column('datasheet_id', UUIDType(), nullable=False),
    Column('owner_id', UUIDType(), nullable=False),
    Column('creation_date_utc', DateTime(timezone=True), nullable=False),
)


class ProjectDao(BaseModel):
    id: UUID
    name: str
    is_staged: bool
    project_def_id: UUID
    datasheet_id: UUID
    owner_id: UUID
    creation_date_utc: datetime


project_container_table = Table(
    "project_container",
    metadata,
    Column('id', UUIDType(), nullable=False, primary_key=True),
    Column('project_id', UUIDType(), nullable=False),
    Column('type_id', UUIDType(), nullable=False),
    Column('path', ARRAY(String, dimensions=1), nullable=False),
    Column('custom_attributes', postgresql.JSON(), nullable=False),
    Column('value', postgresql.JSON(), nullable=True),
    Column('creation_date_utc', DateTime(timezone=True), nullable=False),
)
