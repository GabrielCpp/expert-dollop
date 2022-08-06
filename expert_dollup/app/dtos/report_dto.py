from typing import List, Optional
from uuid import UUID
from datetime import datetime
from expert_dollup.shared.starlette_injection import CamelModel
from .report_definition_dto import ReportRowDictDto
from .dynamic_primitive import PrimitiveUnionDto


class ComputedValueDto(CamelModel):
    label: str
    value: PrimitiveUnionDto
    unit: str


class ReportRowDto(CamelModel):
    node_id: UUID
    formula_id: UUID
    element_def_id: UUID
    child_reference_id: UUID
    columns: List[ComputedValueDto]
    row: ReportRowDictDto


class MinimalReportRowDto(CamelModel):
    node_id: UUID
    formula_id: UUID
    element_def_id: UUID
    child_reference_id: UUID
    columns: List[ComputedValueDto]


class ReportStageDto(CamelModel):
    summary: ComputedValueDto
    rows: List[ReportRowDto]


class MinimalReportStageDto(CamelModel):
    summary: ComputedValueDto
    rows: List[MinimalReportRowDto]


class ReportDto(CamelModel):
    datasheet_id: UUID
    stages: List[ReportStageDto]
    summaries: List[ComputedValueDto]
    creation_date_utc: datetime


class MinimalReportDto(CamelModel):
    stages: List[MinimalReportStageDto]
    summaries: List[ComputedValueDto]
