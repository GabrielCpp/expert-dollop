from typing import List, Optional
from uuid import UUID
from datetime import datetime
from expert_dollup.shared.starlette_injection import CamelModel
from .report_definition_dto import ReportRowDictDto
from .dynamic_primitive import PrimitiveUnionDto


class ComputedValueDto(CamelModel):
    label: str
    value: PrimitiveUnionDto
    unit: Optional[str]
    is_visible: bool


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


class StageColumnDto(CamelModel):
    label: str
    unit: Optional[str]
    is_visible: bool


class ReportStageDto(CamelModel):
    summary: ComputedValueDto
    columns: List[StageColumnDto]
    rows: List[ReportRowDto]


class MinimalReportStageDto(CamelModel):
    summary: ComputedValueDto
    columns: List[StageColumnDto]
    rows: List[MinimalReportRowDto]


class ReportDto(CamelModel):
    name: str
    datasheet_id: UUID
    stages: List[ReportStageDto]
    summaries: List[ComputedValueDto]
    creation_date_utc: datetime


class MinimalReportDto(CamelModel):
    name: str
    stages: List[MinimalReportStageDto]
    summaries: List[ComputedValueDto]
