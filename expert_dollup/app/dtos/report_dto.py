from typing import List, Optional
from uuid import UUID
from datetime import datetime
from expert_dollup.shared.starlette_injection import CamelModel
from .report_definition_dto import ReportRowDictDto
from .dynamic_primitive import PrimitiveUnionDto


class ReportColumnDto(CamelModel):
    value: PrimitiveUnionDto
    unit: Optional[str]


class ReportRowDto(CamelModel):
    project_id: UUID
    report_def_id: UUID
    node_id: UUID
    formula_id: UUID
    group_digest: str
    order_index: int
    datasheet_id: UUID
    element_id: UUID
    child_reference_id: UUID
    columns: List[ReportColumnDto]
    row: ReportRowDictDto


class MinimalReportRowDto(CamelModel):
    node_id: UUID
    formula_id: UUID
    element_id: UUID
    child_reference_id: UUID
    columns: List[ReportColumnDto]


class ReportStageDto(CamelModel):
    label: str
    summary: PrimitiveUnionDto
    rows: List[ReportRowDto]


class MinimalReportStageDto(CamelModel):
    label: str
    summary: PrimitiveUnionDto
    rows: List[MinimalReportRowDto]


class ReportDto(CamelModel):
    stages: List[ReportStageDto]
    creation_date_utc: datetime


class MinimalReportDto(CamelModel):
    stages: List[MinimalReportStageDto]
