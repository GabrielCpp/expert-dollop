from pydantic import BaseModel
from typing import List, Dict, Union, Optional
from uuid import UUID
from datetime import datetime
from .primitives_dao import (
    BoolFieldValueDao,
    IntFieldValueDao,
    StringFieldValueDao,
    DecimalFieldValueDao,
    ReferenceIdDao,
    PrimitiveUnionDao,
)

ReportDefinitionColumnDictDao = Dict[
    str,
    Union[
        BoolFieldValueDao,
        IntFieldValueDao,
        StringFieldValueDao,
        DecimalFieldValueDao,
        ReferenceIdDao,
    ],
]

ReportRowDictDao = Dict[str, ReportDefinitionColumnDictDao]


class ComputedValueDao(BaseModel):
    label: str
    value: PrimitiveUnionDao
    unit: Optional[str]
    is_visible: bool


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
