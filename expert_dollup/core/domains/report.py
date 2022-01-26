from dataclasses import dataclass
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter
from .report_definition import ReportRowDict
from .values_union import PrimitiveUnion


@dataclass
class ReportColumn:
    value: PrimitiveUnion
    unit: Optional[str]


@dataclass
class ComputedValue:
    label: str
    value: PrimitiveUnion
    unit: str


@dataclass
class ReportRow:
    node_id: UUID
    formula_id: UUID
    group_digest: str
    order_index: int
    element_def_id: UUID
    child_reference_id: UUID
    columns: List[ReportColumn]
    row: ReportRowDict

    def __getitem__(self, bucket_name: str):
        return self.row[bucket_name]


@dataclass
class ReportStage:
    summary: ComputedValue
    rows: List[ReportRow]


@dataclass
class Report:
    stages: List[ReportStage]
    summaries: List[ComputedValue]
    creation_date_utc: datetime


@dataclass
class ReportKey:
    project_id: UUID
    report_definition_id: UUID


class ReportRowFilter(QueryFilter):
    project_id: Optional[UUID]
    report_def_id: Optional[UUID]
    group_digest: Optional[str]
    order_index: Optional[int]
    datasheet_id: Optional[UUID]
    element_id: Optional[UUID]
    child_reference_id: Optional[UUID]