from typing import List, Optional, Union
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects import postgresql
from sqlalchemy import Table, MetaData, String, Boolean, DateTime, Column, Binary, Text
from databases import Database
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class PredyktDatabase(Database):
    pass


metadata = MetaData()

project_definition_table = Table(
    'project_definition', metadata,
    Column('id', postgresql.UUID(), nullable=False, primary_key=True),
    Column('name', String, nullable=False),
    Column('default_datasheet_id', postgresql.UUID(), nullable=False),
    Column('plugins', ARRAY(postgresql.UUID(), dimensions=1), nullable=False),
    Column('creation_date_utc', DateTime(timezone=True), nullable=False),
)


class ProjectDefinitionDao(BaseModel):
    id: UUID
    name: str
    default_datasheet_id: UUID
    plugins: List[UUID]
    creation_date_utc: datetime


project_definition_container_table = Table(
    "project_definition_container",
    metadata,
    Column('id', postgresql.UUID(), nullable=False, primary_key=True),
    Column('project_def_id', postgresql.UUID(), nullable=False),
    Column('name', String, nullable=False),
    Column('is_collection', Boolean, nullable=False),
    Column('instanciate_by_default', Boolean, nullable=False),
    Column('custom_attributes', postgresql.JSON(), nullable=False),
    Column('value_type', String, nullable=False),
    Column('default_value', postgresql.JSON(), nullable=True),
    Column('path', String, nullable=False),
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
    path: str
    mixed_paths: List[str]
    creation_date_utc: datetime


project_definition_package_table = Table(
    'project_definition_package',
    metadata,
    Column('id', postgresql.UUID(), nullable=False, primary_key=True),
    Column('project_def_id', postgresql.UUID(), nullable=False),
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
    Column('id', postgresql.UUID(), nullable=False, primary_key=True),
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
    Column('id', postgresql.UUID(), nullable=False, primary_key=True),
    Column('name', String, nullable=False),
    Column('code', Text, nullable=False),
    Column('ast', postgresql.JSON(), nullable=True),
    Column('signature', postgresql.JSON(), nullable=True),
    Column('dependencies', postgresql.JSON(), nullable=True),
    Column('struct_id', postgresql.UUID(), nullable=True),
    Column('package_id', postgresql.UUID(), nullable=True)
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


project_definition_plugin_table = Table(
    "project_definition_plugin", metadata,
    Column('id', postgresql.UUID(), nullable=False, primary_key=True),
    Column('validation_schema', postgresql.JSON(), nullable=False),
    Column('default_config', postgresql.JSON(), nullable=False),
    Column('form_config', postgresql.JSON(), nullable=False),
    Column('name', String, nullable=False),
)


class ProjectDefinitionPluginDao(BaseModel):
    id: UUID
    validation_schema: dict
    default_config: dict
    form_config: dict
    name: str


project_table = Table(
    "project",
    metadata,
    Column('id', postgresql.UUID(), nullable=False, primary_key=True),
    Column('name', String, nullable=False),
    Column('is_staged', Boolean, nullable=False),
    Column('project_def_id', postgresql.UUID(), nullable=True),
    Column('datasheet_id', postgresql.UUID(), nullable=False),
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
    Column('id', postgresql.UUID(), nullable=False, primary_key=True),
    Column('project_id', postgresql.UUID(), nullable=False),
    Column('type_id', postgresql.UUID(), nullable=False),
    Column('path', String, nullable=False),
    Column('custom_attributes', postgresql.JSON(), nullable=False),
    Column('value', postgresql.JSON(), nullable=True),
    Column('creation_date_utc', DateTime(timezone=True), nullable=False),
)


class ProjectContainerDao(BaseModel):
    id: UUID
    project_id: UUID
    type_id: UUID
    path: str
    custom_attributes: dict
    value: dict
    creation_date_utc: datetime


project_container_meta_table = Table(
    "project_container_metadata",
    metadata,
    Column('project_id', postgresql.UUID(), nullable=False),
    Column('type_id', postgresql.UUID(), nullable=False),
    Column('custom_attributes', postgresql.JSON(), nullable=False),
)


class ProjectContainerMetaDao(BaseModel):
    project_id: UUID
    type_id: UUID
    custom_attributes: dict


ressource_table = Table(
    "ressource", metadata,
    Column('id', postgresql.UUID(), nullable=False, primary_key=True),
    Column('owner_id', postgresql.UUID(), nullable=False),
    Column('name', String, nullable=False)
)


class RessourceDao(BaseModel):
    id: UUID
    name: str
    owner_id: UUID


translation_table = Table(
    "translation", metadata,
    Column('ressource_id', postgresql.UUID(),
           nullable=False, primary_key=True),
    Column('locale', String(5), nullable=False, primary_key=True),
    Column('name', String, nullable=False, primary_key=True),
    Column('value', String, nullable=False),
)


class TranslationDao(BaseModel):
    ressource_id: UUID
    locale: str
    name: str
    value: str


setting_table = Table(
    "settings", metadata,
    Column('key', String, nullable=False, primary_key=True),
    Column('value', postgresql.JSON(), nullable=False)
)


class SettingDao(BaseModel):
    key: str
    value: Union[dict, str, bool, int, list]
