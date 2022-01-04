from typing import List
from uuid import UUID
from datetime import datetime
from expert_dollup.shared.starlette_injection import CamelModel
from .report_definition_dto import ReportRowDictDto
from .dynamic_primitive import PrimitiveUnionDto


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
    columns: List[PrimitiveUnionDto]
    row: ReportRowDictDto


class ReportStageDto(CamelModel):
    label: str
    summary: PrimitiveUnionDto
    rows: List[ReportRowDto]


class ReportDto(CamelModel):
    stages: List[ReportStageDto]
    creation_date_utc: datetime
