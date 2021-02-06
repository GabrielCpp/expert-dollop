from typing import List, Optional, Union, Any, Dict
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects import postgresql
from sqlalchemy import (
    Table,
    MetaData,
    String,
    Boolean,
    DateTime,
    Column,
    Binary,
    Text,
    Integer,
)
from sqlalchemy.schema import FetchedValue
from databases import Database
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ExpertDollupDatabase(Database):
    pass


metadata = MetaData()

project_definition_table = Table(
    "project_definition",
    metadata,
    Column("id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("name", String, nullable=False),
    Column("default_datasheet_id", postgresql.UUID(), nullable=False),
    Column("creation_date_utc", DateTime(timezone=True), nullable=False),
)


class ProjectDefinitionDao(BaseModel):
    id: UUID
    name: str
    default_datasheet_id: UUID
    creation_date_utc: datetime


project_definition_container_table = Table(
    "project_definition_container",
    metadata,
    Column("id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("project_def_id", postgresql.UUID(), nullable=False),
    Column("name", String, nullable=False),
    Column("is_collection", Boolean, nullable=False),
    Column("instanciate_by_default", Boolean, nullable=False),
    Column("order_index", Integer, nullable=False),
    Column("config", postgresql.JSON(), nullable=False),
    Column("value_type", String, nullable=False),
    Column("default_value", postgresql.JSON(), nullable=True),
    Column("path", String, nullable=False),
    Column("mixed_paths", ARRAY(String, dimensions=1), nullable=False),
    Column("creation_date_utc", DateTime(timezone=True), nullable=False),
)


class ProjectDefinitionContainerDao(BaseModel):
    id: UUID
    project_def_id: UUID
    name: str
    is_collection: bool
    instanciate_by_default: bool
    order_index: int
    config: dict
    value_type: str
    default_value: Optional[dict]
    path: str
    mixed_paths: List[str]
    creation_date_utc: datetime


project_definition_value_type_table = Table(
    "project_definition_value_type",
    metadata,
    Column("id", String(32), nullable=False, primary_key=True),
    Column("value_json_schema", postgresql.JSON(), nullable=False),
    Column("attributes_json_schema", postgresql.JSON(), nullable=True),
    Column("template_location", String, nullable=True),
    Column("display_name", String, nullable=False),
)


class ProjectDefinitionValueTypeDao(BaseModel):
    id: str
    value_json_schema: dict
    attributes_json_schema: dict
    template_location: Optional[str]
    display_name: str


project_table = Table(
    "project",
    metadata,
    Column("id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("name", String, nullable=False),
    Column("is_staged", Boolean, nullable=False),
    Column("project_def_id", postgresql.UUID(), nullable=True),
    Column("datasheet_id", postgresql.UUID(), nullable=False),
    Column("creation_date_utc", DateTime(timezone=True), nullable=False),
)


class ProjectDao(BaseModel):
    id: UUID
    name: str
    is_staged: bool
    project_def_id: UUID
    datasheet_id: UUID
    creation_date_utc: datetime


project_container_table = Table(
    "project_container",
    metadata,
    Column("id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("project_id", postgresql.UUID(), nullable=False),
    Column("type_id", postgresql.UUID(), nullable=False),
    Column("path", String, nullable=False),
    Column("value", postgresql.JSON(), nullable=True),
    Column("level", Integer, nullable=False, server_default=FetchedValue()),
    Column("mixed_paths", ARRAY(String, dimensions=1), nullable=False),
    Column("creation_date_utc", DateTime(timezone=True), nullable=False),
)


class ProjectContainerDao(BaseModel):
    id: UUID
    project_id: UUID
    type_id: UUID
    path: str
    value: dict
    mixed_paths: List[str]
    creation_date_utc: datetime


project_container_meta_table = Table(
    "project_container_metadata",
    metadata,
    Column("project_id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("type_id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("state", postgresql.JSON(), nullable=False),
)


class ProjectContainerMetaDao(BaseModel):
    project_id: UUID
    type_id: UUID
    state: dict


ressource_table = Table(
    "ressource",
    metadata,
    Column("id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("owner_id", postgresql.UUID(), nullable=False),
    Column("name", String, nullable=False),
)


class RessourceDao(BaseModel):
    id: UUID
    name: str
    owner_id: UUID


translation_table = Table(
    "translation",
    metadata,
    Column("ressource_id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("locale", String(5), nullable=False, primary_key=True),
    Column("name", String, nullable=False, primary_key=True),
    Column("value", String, nullable=False),
)


class TranslationDao(BaseModel):
    ressource_id: UUID
    locale: str
    name: str
    value: str


setting_table = Table(
    "settings",
    metadata,
    Column("key", String, nullable=False, primary_key=True),
    Column("value", postgresql.JSON(), nullable=False),
)


class SettingDao(BaseModel):
    key: str
    value: Union[dict, str, bool, int, list]
