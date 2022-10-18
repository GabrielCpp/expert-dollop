from typing import List, Optional, Union, Dict
from typing_extensions import TypeAlias
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, StrictStr, StrictFloat, StrictBool, StrictInt
from expert_dollup.shared.database_services import (
    DbConnection,
    DaoMappingConfig,
    DaoVersioning,
    DaoTypeAnnotation,
)
from .node_config_dao import (
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
    AggregateReferenceConfigDao,
)

ROOT_LEVEL = 0
SECTION_LEVEL = 1
FORM_LEVEL = 2
FORM_SECTION_LEVEL = 3
FIELD_LEVEL = 4
FORMULA_TYPE = "formula"
DEFINITION_NODE_TYPE = "definition_node"


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


PrimitiveWithNoneUnionDao: TypeAlias = Union[
    BoolFieldValueDao, IntFieldValueDao, StringFieldValueDao, DecimalFieldValueDao, None
]

PrimitiveUnionDao: TypeAlias = Union[
    BoolFieldValueDao, IntFieldValueDao, StringFieldValueDao, DecimalFieldValueDao
]

PrimitiveWithReferenceDaoUnion = Union[
    BoolFieldValueDao,
    IntFieldValueDao,
    StringFieldValueDao,
    DecimalFieldValueDao,
    ReferenceIdDao,
]


class ProjectDefinitionDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "project_definition"

    id: UUID
    name: str = Field(max_length=64)
    creation_date_utc: datetime


class FormulaDependencyDao(BaseModel):
    target_type_id: UUID
    name: str = Field(max_length=64)


class FormulaDependencyGraphDao(BaseModel):
    formulas: List[FormulaDependencyDao]
    nodes: List[FormulaDependencyDao]


class FormulaConfigDao(BaseModel):
    expression: str
    dependency_graph: FormulaDependencyGraphDao
    attached_to_type_id: UUID


class ProjectDefinitionFormulaDao(BaseModel):
    class Meta:
        pk = "id"
        dao_mapping_details = DaoMappingConfig(
            versioning=DaoVersioning(latest_version=1, version_mappers={}),
            typed=DaoTypeAnnotation(
                kind=FORMULA_TYPE, is_my_kind=lambda d: "expression" in d["config"]
            ),
        )

    class Config:
        title = "project_definition_node"

    id: UUID
    project_definition_id: UUID
    name: str = Field(max_length=64)
    path: str
    level: int
    display_query_internal_id: UUID
    creation_date_utc: datetime
    config: FormulaConfigDao


class DefinitionNodeConfigDao(BaseModel):
    is_collection: bool
    instanciate_by_default: bool
    ordinal: int
    translations: TranslationConfigDao
    triggers: List[TriggerDao]
    meta: NodeMetaConfigDao
    field_details: Optional[FieldDetailsUnionDao]


class ProjectDefinitionNodeDao(BaseModel):
    class Meta:
        pk = "id"
        dao_mapping_details = DaoMappingConfig(
            versioning=DaoVersioning(latest_version=1, version_mappers={}),
            typed=DaoTypeAnnotation(
                kind=DEFINITION_NODE_TYPE,
                is_my_kind=lambda d: "field_details" in d["config"],
            ),
        )

        options = {
            "firestore": {
                "collection_count": False,
                "key_counts": set([frozenset(["project_definition_id"])]),
            }
        }

    class Config:
        title = "project_definition_node"

    id: UUID
    project_definition_id: UUID
    name: str = Field(max_length=64)
    path: str
    level: int
    display_query_internal_id: UUID
    creation_date_utc: datetime
    config: DefinitionNodeConfigDao


class ProjectDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "project"

    id: UUID
    name: str = Field(max_length=64)
    is_staged: bool
    project_definition_id: UUID
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


class AggregateAttributeDao(BaseModel):
    name: str
    is_readonly: bool
    value: PrimitiveWithReferenceDaoUnion


class AggregateDao(BaseModel):
    id: UUID
    ordinal: int
    name: str
    is_extendable: bool
    attributes: List[AggregateAttributeDao]


class NodeReferenceConfigDao(BaseModel):
    node_type: str


class AggregateAttributeSchema(BaseModel):
    name: str
    details: Union[
        IntFieldConfigDao,
        DecimalFieldConfigDao,
        StringFieldConfigDao,
        BoolFieldConfigDao,
        AggregateReferenceConfigDao,
        NodeReferenceConfigDao,
    ]


class AggregateCollectionDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "datasheet_definition_aggregate_collection"

    id: UUID
    project_definition_id: UUID
    name: str = Field(max_length=64)
    is_abstract: bool = False
    attributes_schema: List[AggregateAttributeSchema]
    aggregates: List[AggregateDao]


class DatasheetDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "datasheet"

    id: UUID
    name: str = Field(max_length=64)
    is_staged: bool
    project_definition_id: UUID
    from_datasheet_id: Optional[UUID]
    creation_date_utc: datetime


class AttributeDao(BaseModel):
    name: str
    value: PrimitiveWithReferenceUnion


class DatasheetElementDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "datasheet_element"

    id: UUID
    datasheet_id: UUID
    aggregate_id: UUID
    ordinal: int
    attributes: List[AttributeDao]
    original_datasheet_id: UUID
    original_owner_organization_id: UUID
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


class ReportComputationDao(BaseModel):
    name: str = Field(max_length=64)
    expression: str
    unit: Union[StrictStr, AttributeBucketDao, None]
    is_visible: bool


class StageSummaryDao(BaseModel):
    label: AttributeBucketDao
    summary: ReportComputationDao


class ReportStructureDao(BaseModel):
    datasheet_selection_alias: str
    formula_attribute: AttributeBucketDao
    datasheet_attribute: AttributeBucketDao
    joins_cache: List[ReportJoinDao]
    columns: List[ReportComputationDao]
    group_by: List[AttributeBucketDao]
    order_by: List[AttributeBucketDao]
    stage_summary: StageSummaryDao
    report_summary: List[ReportComputationDao]


class ReportDefinitionDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "report_definition"

    id: UUID
    project_definition_id: UUID
    name: str = Field(max_length=64)
    structure: ReportStructureDao
    distributable: bool


class MeasureUnitDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "unit"

    id: str = Field(max_length=16)


class ComputedValueDao(BaseModel):
    label: str
    value: PrimitiveUnionDao
    unit: Optional[str]
    is_visible: bool


class SuppliedItemDao(BaseModel):
    datasheet_id: UUID
    element_def_id: UUID
    child_reference_id: UUID
    organization_id: UUID


class DistributableItemDao(BaseModel):
    class Meta:
        pk = ("project_id", "node_id", "formula_id")

    class Config:
        title = "distributable_items"

    project_id: UUID
    report_definition_id: UUID
    node_id: UUID
    formula_id: UUID
    supplied_item: SuppliedItemDao
    distribution_ids: List[UUID]

    summary: ComputedValueDao
    columns: List[ComputedValueDao]
    obsolete: bool
    creation_date_utc: datetime
