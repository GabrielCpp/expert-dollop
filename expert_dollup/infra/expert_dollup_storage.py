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
)
from .storage_connectors.storage_client import StorageClient


class ExpertDollupStorage(StorageClient):
    pass


class UnitInstanceDao(BaseModel):
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


class ComputedValueDao(BaseModel):
    label: str
    value: PrimitiveUnionDao
    unit: str


class ReportRowDao(BaseModel):
    node_id: UUID
    formula_id: UUID
    element_def_id: UUID
    child_reference_id: UUID
    columns: List[ComputedValueDao]
    row: ReportRowDictDao


class ReportStageDao(BaseModel):
    summary: ComputedValueDao
    rows: List[ReportRowDao]


class ReportDao(BaseModel):
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
