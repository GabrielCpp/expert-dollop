from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List, Dict, Union
from datetime import datetime
from .expert_dollup_db import (
    PrimitiveUnionDao,
    BoolFieldValueDao,
    IntFieldValueDao,
    StringFieldValueDao,
    DecimalFieldValueDao,
    ReferenceIdDao,
    FormulaDependencyGraphDao,
    ComputedValueDao,
)
from expert_dollup.shared.database_services import StorageClient


class ExpertDollupStorage(StorageClient):
    pass


class UnitDao(BaseModel):
    formula_id: Optional[UUID]
    node_id: UUID
    node_path: List[UUID]
    name: str
    calculation_details: str
    result: PrimitiveUnionDao


ReportDefinitionColumnDictDao = Dict[
    str,
    Union[
        List[ReferenceIdDao],
        BoolFieldValueDao,
        IntFieldValueDao,
        StringFieldValueDao,
        DecimalFieldValueDao,
        ReferenceIdDao,
    ],
]
ReportRowDictDao = Dict[str, ReportDefinitionColumnDictDao]
ReportRowsCacheDao = List[ReportRowDictDao]


class ReportRowDao(BaseModel):
    node_id: UUID
    formula_id: UUID
    aggregate_id: UUID
    element_id: UUID
    columns: List[ComputedValueDao]
    row: ReportRowDictDao


class StageColumnDao(BaseModel):
    label: str
    unit: Optional[str]
    is_visible: bool


class ReportStageDao(BaseModel):
    summary: ComputedValueDao
    columns: List[StageColumnDao]
    rows: List[ReportRowDao]


class ReportDao(BaseModel):
    name: str
    datasheet_id: UUID
    stages: List[ReportStageDao]
    summaries: List[ComputedValueDao]
    creation_date_utc: datetime


class StagedFormulaDao(BaseModel):
    id: UUID
    project_definition_id: UUID
    attached_to_type_id: UUID
    name: str = Field(max_length=64)
    expression: str
    final_ast: dict
    dependency_graph: FormulaDependencyGraphDao
