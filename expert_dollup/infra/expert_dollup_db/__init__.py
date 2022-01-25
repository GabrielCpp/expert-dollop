from typing import List, Optional, Union, Dict
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, StrictStr, StrictFloat, StrictBool, StrictInt
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


class IntFieldValueDao(BaseModel):
    integer: int


class DecimalFieldValueDao(BaseModel):
    numeric: Decimal


class StringFieldValueDao(BaseModel):
    text: str


class BoolFieldValueDao(BaseModel):
    enabled: bool


class ReferenceIdDao(BaseModel):
    uuid: UUID


class ReferenceIdDao(BaseModel):
    uuid: UUID


PrimitiveWithNoneUnionDao = Union[
    BoolFieldValueDao, IntFieldValueDao, StringFieldValueDao, DecimalFieldValueDao, None
]

PrimitiveUnionDao = Union[
    BoolFieldValueDao, IntFieldValueDao, StringFieldValueDao, DecimalFieldValueDao
]


LabelAttributeDaoUnion = Union[
    BoolFieldValueDao,
    IntFieldValueDao,
    StringFieldValueDao,
    DecimalFieldValueDao,
    ReferenceIdDao,
]

JsonSchemaDao = dict


class ProjectDefinitionDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "project_definition"

    id: UUID
    name: str = Field(max_length=64)
    default_datasheet_id: UUID
    datasheet_def_id: UUID
    creation_date_utc: datetime


class ProjectDefinitionNodeDao(BaseModel):
    class Meta:
        pk = "id"
        version = 1
        version_mappers = {}
        options = {
            "firestore": {
                "collection_count": False,
                "key_counts": set([frozenset(["project_def_id"])]),
            }
        }

    class Config:
        title = "project_definition_node"

    id: UUID
    project_def_id: UUID
    name: str = Field(max_length=64)
    is_collection: bool
    instanciate_by_default: bool
    order_index: int
    config: NodeConfigDao
    default_value: PrimitiveWithNoneUnionDao
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
    name: str = Field(max_length=64)
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
    type_name: str = Field(max_length=64)
    path: str
    value: PrimitiveWithNoneUnionDao
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
    kind: str = Field(max_length=64)
    owner_id: UUID


class TranslationDao(BaseModel):
    class Meta:
        pk = ("ressource_id", "scope", "locale", "name")
        options = {
            "firestore": {
                "collection_count": True,
                "key_counts": set(
                    [frozenset(["ressource_id"]), frozenset(["ressource_id", "locale"])]
                ),
            }
        }

    class Config:
        title = "translation"

    id: UUID
    ressource_id: UUID
    locale: str = Field(min_length=5, max_length=5)
    scope: UUID
    name: str = Field(max_length=64)
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
    name: str = Field(max_length=64)


class FormulaDependencyGraphDao(BaseModel):
    formulas: List[FormulaDependencyDao]
    nodes: List[FormulaDependencyDao]


class ProjectDefinitionFormulaDao(BaseModel):
    class Meta:
        pk = "id"
        options = {
            "firestore": {
                "collection_count": False,
                "key_counts": set([frozenset(["project_def_id"])]),
            }
        }

    class Config:
        title = "project_definition_formula"

    id: UUID
    project_def_id: UUID
    attached_to_type_id: UUID
    name: str = Field(max_length=64)
    expression: str
    dependency_graph: FormulaDependencyGraphDao


class ElementPropertySchemaDao(BaseModel):
    value_validator: JsonSchemaDao


class DatasheetDefinitionDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "datasheet_definition"

    id: UUID
    name: str = Field(max_length=64)
    properties: Dict[str, ElementPropertySchemaDao]


class CollectionAggregateDao(BaseModel):
    from_collection: str


class DatasheetAggregateDao(BaseModel):
    from_datasheet: str


class FormulaAggregateDao(BaseModel):
    from_formula: str


class StaticPropertyDao(BaseModel):
    json_schema: JsonSchemaDao


LabelAttributeSchemaDaoUnion = Union[
    StaticPropertyDao,
    CollectionAggregateDao,
    DatasheetAggregateDao,
    FormulaAggregateDao,
]


class LabelCollectionDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "datasheet_definition_label_collection"

    id: UUID
    datasheet_definition_id: UUID
    name: str = Field(max_length=64)
    attributes_schema: Dict[str, LabelAttributeSchemaDaoUnion]


class LabelDao(BaseModel):
    class Meta:
        pk = "id"
        options = {
            "firestore": {
                "collection_count": False,
                "key_counts": set([frozenset(["label_collection_id"])]),
            }
        }

    class Config:
        title = "datasheet_definition_label"

    id: UUID
    label_collection_id: UUID
    order_index: int
    name: str = Field(max_length=64)
    attributes: Dict[str, LabelAttributeDaoUnion]


class DatasheetDefinitionElementPropertyDao(BaseModel):
    is_readonly: bool
    value: PrimitiveUnionDao


class DatasheetDefinitionElementDao(BaseModel):
    class Meta:
        pk = "id"
        options = {
            "firestore": {
                "collection_count": False,
                "key_counts": set([frozenset(["datasheet_def_id"])]),
            }
        }

    class Config:
        title = "datasheet_definition_element"

    id: UUID
    unit_id: str
    is_collection: bool
    name: str = Field(max_length=64)
    datasheet_def_id: UUID
    order_index: int
    default_properties: Dict[str, DatasheetDefinitionElementPropertyDao]
    tags: List[UUID]
    creation_date_utc: datetime


class DatasheetDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "datasheet"

    id: UUID
    name: str = Field(max_length=64)
    is_staged: bool
    datasheet_def_id: UUID
    from_datasheet_id: Optional[UUID]
    creation_date_utc: datetime


class DatasheetElementDao(BaseModel):
    class Meta:
        pk = ("datasheet_id", "element_def_id", "child_element_reference")
        options = {
            "firestore": {
                "collection_count": False,
                "key_counts": set(
                    [
                        frozenset(["datasheet_id"]),
                        frozenset(["datasheet_id", "element_def_id"]),
                    ]
                ),
            }
        }

    class Config:
        title = "datasheet_element"

    datasheet_id: UUID
    element_def_id: UUID
    child_element_reference: UUID
    properties: Dict[str, PrimitiveUnionDao]
    original_datasheet_id: UUID
    creation_date_utc: datetime


class ReportJoinDao(BaseModel):
    from_object_name: str = Field(max_length=64)
    from_property_name: str = Field(max_length=64)
    join_on_collection: str = Field(max_length=64)
    join_on_attribute: str = Field(max_length=64)
    alias_name: str = Field(max_length=64)
    warn_about_idle_items: bool
    same_cardinality: bool
    allow_dicard_element: bool


class AttributeBucketDao(BaseModel):
    bucket_name: str = Field(max_length=64)
    attribute_name: str = Field(max_length=64)


class ReportDefinitionColumnDao(BaseModel):
    name: str = Field(max_length=64)
    expression: str
    is_visible: bool
    unit_id: Optional[str] = None
    unit: Optional[AttributeBucketDao] = None


class ReportComputationDao(BaseModel):
    expression: str
    unit_id: Optional[str] = None


class StageGroupingDao(BaseModel):
    label: AttributeBucketDao
    summary: ReportComputationDao


class ReportStructureDao(BaseModel):
    datasheet_selection_alias: str
    formula_attribute: AttributeBucketDao
    datasheet_attribute: AttributeBucketDao
    joins_cache: List[ReportJoinDao]
    columns: List[ReportDefinitionColumnDao]
    group_by: List[AttributeBucketDao]
    order_by: List[AttributeBucketDao]
    stage: StageGroupingDao


class ReportDefinitionDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "report_definition"

    id: UUID
    project_def_id: UUID
    name: str = Field(max_length=64)
    structure: ReportStructureDao


class MeasureUnitDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "unit"

    id: str = Field(max_length=16)