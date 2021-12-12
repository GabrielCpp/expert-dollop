from typing import List, Optional, Union, Dict
from uuid import UUID
from datetime import datetime
from pydantic import StrictBool, StrictInt, StrictStr, StrictFloat, BaseModel, Field
from expert_dollup.shared.database_services import DbConnection
from .node_config_dao import (
    NodeConfigDao,
    TranslationConfigDao,
    TriggerDao,
    NodeMetaConfigDao,
    FieldDetailsUnionDao,
    StaticNumberFieldConfigDao,
    CollapsibleContainerFieldConfigDao,
    StaticChoiceFieldConfigDao,
    StaticChoiceOptionDao,
    BoolFieldConfigDao,
    StringFieldConfigDao,
    DecimalFieldConfigDao,
    IntFieldConfigDao,
)

ROOT_LEVEL = 0
SECTION_LEVEL = 1
FORM_LEVEL = 2
FORM_SECTION_LEVEL = 3
FIELD_LEVEL = 4


class ExpertDollupDatabase(DbConnection):
    pass


ValueUnion = Union[StrictBool, StrictInt, StrictStr, StrictFloat, None]
JsonSchemaDao = dict


class ProjectDefinitionDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "project_definition"

    id: UUID
    name: str
    default_datasheet_id: UUID
    datasheet_def_id: UUID
    creation_date_utc: datetime


class ProjectDefinitionNodeDao(BaseModel):
    class Meta:
        pk = "id"
        version = 1
        version_mappers = {}

    class Config:
        title = "project_definition_node"

    id: UUID
    project_def_id: UUID
    name: str
    is_collection: bool
    instanciate_by_default: bool
    order_index: int
    config: NodeConfigDao
    default_value: ValueUnion
    path: str
    level: int
    display_query_internal_id: UUID
    creation_date_utc: datetime


class ProjectDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "project"

    id: UUID
    name: str
    is_staged: bool
    project_def_id: UUID
    datasheet_id: UUID
    creation_date_utc: datetime


class ProjectNodeDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "project_node"

    id: UUID
    project_id: UUID
    type_id: UUID
    type_name: str
    path: str
    value: ValueUnion
    label: str
    level: int
    type_path: str
    display_query_internal_id: UUID
    creation_date_utc: datetime


class ProjectNodeMetaStateDao(BaseModel):
    is_visible: bool
    selected_child: Optional[UUID]


class ProjectNodeMetaDao(BaseModel):
    class Meta:
        pk = ("project_id", "type_id")

    class Config:
        title = "project_node_metadata"

    project_id: UUID
    type_id: UUID
    state: ProjectNodeMetaStateDao
    definition: ProjectDefinitionNodeDao
    display_query_internal_id: UUID


class RessourceDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "ressource"

    id: UUID
    name: str
    owner_id: UUID


class TranslationDao(BaseModel):
    class Meta:
        pk = ("ressource_id", "scope", "locale", "name")

    class Config:
        title = "translation"

    id: UUID
    ressource_id: UUID
    locale: str = Field(min_length=5, max_length=5)
    scope: UUID
    name: str
    value: str
    creation_date_utc: datetime


class SettingDao(BaseModel):
    class Meta:
        pk = "key"

    class Config:
        title = "settings"

    key: str
    value: Union[dict, str, bool, int, list]


class FormulaDependencyDao(BaseModel):
    target_type_id: UUID


class FormulaDependencyGraphDao(BaseModel):
    formulas: List[FormulaDependencyDao]
    nodes: List[FormulaDependencyDao]


class ProjectDefinitionFormulaDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "project_definition_formula"

    id: UUID
    project_def_id: UUID
    attached_to_type_id: UUID
    name: str
    expression: str
    dependency_graph: FormulaDependencyGraphDao


class ProjectFormulaCacheDao(BaseModel):
    class Meta:
        pk = ("project_id", "formula_id", "node_id")

    class Config:
        title = "project_node_formula_cache"

    project_id: UUID
    formula_id: UUID
    node_id: UUID
    calculation_details: str
    result: Union[int, str, float, bool]
    last_modified_date_utc: datetime


class UnitDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "unit"

    id: str = Field(max_length=16)


class ElementPropertySchemaDao(BaseModel):
    value_validator: JsonSchemaDao


class DatasheetDefinitionDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "datasheet_definition"

    id: UUID
    name: str
    properties: Dict[str, ElementPropertySchemaDao]


class CollectionAggregateDao(BaseModel):
    from_collection: str


class DatasheetAggregateDao(BaseModel):
    from_datasheet: str


class FormulaAggregateDao(BaseModel):
    from_formula: str


AcceptedAggregateDaoUnion = Union[
    CollectionAggregateDao, DatasheetAggregateDao, FormulaAggregateDao
]


class LabelCollectionDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "datasheet_definition_label_collection"

    id: UUID
    datasheet_definition_id: UUID
    name: str
    properties_schema: Dict[str, JsonSchemaDao]
    accepted_aggregates: Dict[str, AcceptedAggregateDaoUnion]


class LabelDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "datasheet_definition_label"

    id: UUID
    label_collection_id: UUID
    order_index: int
    properties: Dict[str, ValueUnion]
    aggregates: Dict[str, UUID]


class DatasheetDefinitionElementPropertyDao(BaseModel):
    is_readonly: bool
    value: ValueUnion


class DatasheetDefinitionElementDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "datasheet_definition_element"

    id: UUID
    unit_id: str
    is_collection: bool
    name: str = Field(max_length=64)
    datasheet_def_id: UUID
    order_index: int
    default_properties: Dict[str, DatasheetDefinitionElementPropertyDao]
    tags: List[str]
    creation_date_utc: datetime


class DatasheetDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "datasheet"

    id: UUID
    name: str
    is_staged: bool
    datasheet_def_id: UUID
    from_datasheet_id: Optional[UUID]
    creation_date_utc: datetime


class DatasheetElementDao(BaseModel):
    class Meta:
        pk = ("datasheet_id", "element_def_id", "child_element_reference")

    class Config:
        title = "datasheet_element"

    datasheet_id: UUID
    element_def_id: UUID
    child_element_reference: UUID
    properties: dict
    original_datasheet_id: UUID
    creation_date_utc: datetime


class ReportJoinDao(BaseModel):
    to_object_name: str
    from_object_name: str
    join_on_property_name: str
    join_type: str


class ReportStructureDao(BaseModel):
    initial_selection: ReportJoinDao
    joins: List[ReportJoinDao]


class ReportDefinitionDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "report_definition"

    id: UUID
    project_def_id: UUID
    name: str
    structure: ReportStructureDao