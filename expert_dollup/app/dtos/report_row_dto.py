from uuid import UUID
from expert_dollup.shared.starlette_injection import CamelModel
from .report_definition_dto import ReportRowDictDto, ReportColumnDictDto


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
    row: ReportRowDictDto


class ReportLightRowDto(CamelModel):
    node_id: UUID
    formula_id: UUID
    order_index: int
    element_id: UUID
    child_reference_id: UUID
    columns: ReportColumnDictDto