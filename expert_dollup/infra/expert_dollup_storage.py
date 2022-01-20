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


ReportColumnDictDao = Dict[
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
ReportRowDictDao = Dict[str, ReportColumnDictDao]
ReportRowsCacheDao = List[ReportRowDictDao]


class ReportRowDao(BaseModel):
    project_id: UUID
    report_def_id: UUID
    node_id: UUID
    formula_id: UUID
    group_digest: str
    order_index: int
    datasheet_id: UUID
    element_id: UUID
    child_reference_id: UUID
    columns: List[PrimitiveUnionDao]
    row: ReportRowDictDao


class ReportStageDao(BaseModel):
    label: str
    summary: PrimitiveUnionDao
    rows: List[ReportRowDao]


class ReportDao(BaseModel):
    stages: List[ReportStageDao]
    creation_date_utc: datetime


class StagedFormulaDao(BaseModel):

    id: UUID
    project_def_id: UUID
    attached_to_type_id: UUID
    name: str = Field(max_length=64)
    expression: str
    final_ast: dict
    dependency_graph: FormulaDependencyGraphDao