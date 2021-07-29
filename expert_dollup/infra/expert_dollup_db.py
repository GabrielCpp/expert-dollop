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
    Text,
    Integer,
)
from sqlalchemy.schema import FetchedValue
from databases import Database
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

ROOT_LEVEL = 0
SECTION_LEVEL = 1
FORM_LEVEL = 2
FORM_SECTION_LEVEL = 3
FIEL_LEVEL = 4


class ExpertDollupDatabase(Database):
    pass


metadata = MetaData()

project_definition_table = Table(
    "project_definition",
    metadata,
    Column("id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("name", String, nullable=False),
    Column("default_datasheet_id", postgresql.UUID(), nullable=False),
    Column("datasheet_def_id", postgresql.UUID(), nullable=False),
    Column("creation_date_utc", DateTime(timezone=True), nullable=False),
)


class ProjectDefinitionDao(BaseModel):
    id: UUID
    name: str
    default_datasheet_id: UUID
    datasheet_def_id: UUID
    creation_date_utc: datetime


project_definition_node_table = Table(
    "project_definition_node",
    metadata,
    Column("id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("project_def_id", postgresql.UUID(), nullable=False),
    Column("name", String, nullable=False),
    Column("is_collection", Boolean, nullable=False),
    Column("instanciate_by_default", Boolean, nullable=False),
    Column("order_index", Integer, nullable=False),
    Column("config", String, nullable=False),
    Column("default_value", String, nullable=True),
    Column("path", String, nullable=False),
    Column("display_query_internal_id", postgresql.UUID(), nullable=False),
    Column("level", Integer, nullable=False),
    Column("creation_date_utc", DateTime(timezone=True), nullable=False),
)


class ProjectDefinitionNodeDao(BaseModel):
    id: UUID
    project_def_id: UUID
    name: str
    is_collection: bool
    instanciate_by_default: bool
    order_index: int
    config: str
    default_value: Optional[str]
    path: str
    level: int
    display_query_internal_id: UUID
    creation_date_utc: datetime


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


project_node_table = Table(
    "project_node",
    metadata,
    Column("id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("project_id", postgresql.UUID(), nullable=False),
    Column("type_id", postgresql.UUID(), nullable=False),
    Column("path", String, nullable=False),
    Column("value", String, nullable=True),
    Column("label", String, nullable=True),
    Column("level", Integer, nullable=False),
    Column("type_path", String, nullable=False),
    Column("display_query_internal_id", postgresql.UUID(), nullable=False),
    Column("creation_date_utc", DateTime(timezone=True), nullable=False),
)


class ProjectNodeDao(BaseModel):
    id: UUID
    project_id: UUID
    type_id: UUID
    path: str
    value: Optional[str]
    label: Optional[str]
    level: int
    type_path: str
    display_query_internal_id: UUID
    creation_date_utc: datetime


project_node_meta_table = Table(
    "project_node_metadata",
    metadata,
    Column("project_id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("type_id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("state", String, nullable=False),
    Column("definition", String, nullable=False),
    Column("display_query_internal_id", postgresql.UUID(), nullable=False),
)


class ProjectNodeMetaStateDao(BaseModel):
    is_visible: bool
    selected_child: Optional[UUID]


class ProjectNodeMetaDao(BaseModel):
    project_id: UUID
    type_id: UUID
    state: str
    definition: str
    display_query_internal_id: UUID


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
    Column("id", postgresql.UUID(), nullable=False),
    Column("ressource_id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("scope", postgresql.UUID(), nullable=False, primary_key=True),
    Column("locale", String(5), nullable=False, primary_key=True),
    Column("name", String, nullable=False, primary_key=True),
    Column("value", String, nullable=False),
    Column("creation_date_utc", DateTime(timezone=True), nullable=False),
)


class TranslationDao(BaseModel):
    id: UUID
    ressource_id: UUID
    locale: str
    scope: UUID
    name: str
    value: str
    creation_date_utc: datetime


setting_table = Table(
    "settings",
    metadata,
    Column("key", String, nullable=False, primary_key=True),
    Column("value", postgresql.JSON(), nullable=False),
)


class SettingDao(BaseModel):
    key: str
    value: Union[dict, str, bool, int, list]


project_definition_formula_table = Table(
    "project_definition_formula",
    metadata,
    Column("id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("project_def_id", postgresql.UUID(), nullable=False),
    Column("attached_to_type_id", postgresql.UUID(), nullable=False),
    Column("name", String, nullable=False),
    Column("expression", String, nullable=False),
    Column("generated_ast", String, nullable=False),
)


class ProjectDefinitionFormulaDao(BaseModel):
    id: UUID
    project_def_id: UUID
    attached_to_type_id: UUID
    name: str
    expression: str
    generated_ast: str


project_definition_formula_dependency_table = Table(
    "project_definition_formula_dependencies",
    metadata,
    Column("formula_id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("depend_on_formula_id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("project_def_id", postgresql.UUID(), nullable=False),
)


class ProjectDefinitionFormulaDependencyDao(BaseModel):
    formula_id: UUID
    depend_on_formula_id: UUID
    project_def_id: UUID


project_definition_formula_node_dependency_table = Table(
    "project_definition_formula_node_dependencies",
    metadata,
    Column("formula_id", postgresql.UUID(), nullable=False, primary_key=True),
    Column(
        "depend_on_node_id",
        postgresql.UUID(),
        nullable=False,
        primary_key=True,
    ),
    Column("project_def_id", postgresql.UUID(), nullable=False),
)


class ProjectDefinitionFormulaContainerDependencyDao(BaseModel):
    formula_id: UUID
    depend_on_node_id: UUID
    project_def_id: UUID


project_formula_cache_table = Table(
    "project_node_formula_cache",
    metadata,
    Column("project_id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("formula_id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("node_id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("calculation_details", String, nullable=False),
    Column("result", postgresql.JSON(), nullable=False),
    Column("last_modified_date_utc", DateTime(timezone=True), nullable=False),
)


class ProjectFormulaCacheDao(BaseModel):
    project_id: UUID
    formula_id: UUID
    node_id: UUID
    calculation_details: str
    result: Any
    last_modified_date_utc: datetime


unit_table = Table(
    "unit",
    metadata,
    Column("id", postgresql.UUID(), nullable=False, primary_key=True),
)


class UnitDao(BaseModel):
    id: UUID


datasheet_definition_table = Table(
    "datasheet_definition",
    metadata,
    Column("id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("name", String, nullable=False),
    Column("properties", String(), nullable=False),
)

JsonSchemaDao = dict


class ElementPropertySchemaDao:
    value_validator: JsonSchemaDao


class DatasheetDefinitionDao(BaseModel):
    id: UUID
    name: str
    properties: str


datasheet_definition_label_collection_table = Table(
    "datasheet_definition_label_collection",
    metadata,
    Column("id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("datasheet_definition_id", postgresql.UUID(), nullable=False),
    Column("name", String, nullable=False),
)


class LabelCollectionDao(BaseModel):
    id: UUID
    datasheet_definition_id: UUID
    name: str


datasheet_definition_label_table = Table(
    "datasheet_definition_label",
    metadata,
    Column("id", postgresql.UUID(), nullable=False, primary_key=True),
    Column(
        "label_collection_id",
        postgresql.UUID(),
        nullable=False,
    ),
    Column("order_index", Integer, nullable=False),
)


class LabelDao(BaseModel):
    id: UUID
    label_collection_id: UUID
    order_index: int


datasheet_definition_element_table = Table(
    "datasheet_definition_element",
    metadata,
    Column("id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("unit_id", postgresql.UUID(), nullable=False),
    Column("name", String(64), nullable=False),
    Column("is_collection", Boolean, nullable=False),
    Column("datasheet_def_id", postgresql.UUID(), nullable=False),
    Column("order_index", Integer, nullable=False),
    Column("default_properties", postgresql.JSON(), nullable=False),
    Column("tags", ARRAY(String, dimensions=1), nullable=False),
    Column("creation_date_utc", DateTime(timezone=True), nullable=False),
)


class DatasheetDefinitionElementDao(BaseModel):
    id: UUID
    unit_id: str
    is_collection: bool
    name: str
    datasheet_def_id: UUID
    order_index: int
    default_properties: dict
    tags: List[str]
    creation_date_utc: datetime


datasheet_table = Table(
    "datasheet",
    metadata,
    Column("id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("name", String, nullable=False),
    Column("is_staged", Boolean, nullable=False),
    Column("datasheet_def_id", postgresql.UUID(), nullable=False),
    Column("from_datasheet_id", postgresql.UUID(), nullable=True),
    Column("creation_date_utc", DateTime(timezone=True), nullable=False),
)


class DatasheetDao(BaseModel):
    id: UUID
    name: str
    is_staged: bool
    datasheet_def_id: UUID
    from_datasheet_id: UUID
    creation_date_utc: datetime


datasheet_element_table = Table(
    "datasheet_element",
    metadata,
    Column("datasheet_id", postgresql.UUID(), nullable=False, primary_key=True),
    Column("element_def_id", postgresql.UUID(), nullable=False, primary_key=True),
    Column(
        "child_element_reference",
        postgresql.UUID(),
        nullable=False,
        primary_key=True,
    ),
    Column("properties", postgresql.JSON(), nullable=False),
    Column("original_datasheet_id", postgresql.UUID(), nullable=False),
    Column("creation_date_utc", DateTime(timezone=True), nullable=False),
)


class DatasheetElementDao(BaseModel):
    datasheet_id: UUID
    element_def_id: UUID
    child_element_reference: UUID
    properties: dict
    original_datasheet_id: UUID
    creation_date_utc: datetime
