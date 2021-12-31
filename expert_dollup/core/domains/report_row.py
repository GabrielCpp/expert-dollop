from dataclasses import dataclass
from uuid import UUID
from typing import List, Optional, Union
from expert_dollup.shared.database_services import QueryFilter
from .report_definition import ReportRowDict


@dataclass
class ReportRow:
    project_id: UUID
    report_def_id: UUID
    node_id: UUID
    formula_id: UUID
    group_digest: str
    order_index: int
    datasheet_id: UUID
    element_id: UUID
    child_reference_id: UUID
    row: ReportRowDict


@dataclass
class ReportGroup:
    label: str
    summary: Union[float, str, bool, int]
    rows: List[ReportRow]


class ReportRowFilter(QueryFilter):
    project_id: Optional[UUID]
    report_def_id: Optional[UUID]
    group_digest: Optional[str]
    order_index: Optional[int]
    datasheet_id: Optional[UUID]
    element_id: Optional[UUID]
    child_reference_id: Optional[UUID]