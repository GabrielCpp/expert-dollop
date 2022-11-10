from dataclasses import dataclass
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter
from .definition.report_definition import ReportRowDict
from .values_union import PrimitiveUnion


@dataclass
class ComputedValue:
    label: str
    value: PrimitiveUnion
    unit: Optional[str]
    is_visible: bool = True

    @property
    def key(self) -> str:
        return f"{self.label}:{self.value}/{self.unit}"


@dataclass
class ReportRow:
    node_id: UUID
    formula_id: UUID
    aggregate_id: UUID
    element_id: UUID
    columns: List[ComputedValue]
    row: ReportRowDict

    def __getitem__(self, bucket_name: str):
        if not bucket_name in self.row:
            raise KeyError(bucket_name, list(self.row.keys()))

        return self.row[bucket_name]


@dataclass
class StageColumn:
    label: str
    unit: Optional[str]
    is_visible: bool = True


@dataclass
class ReportStage:
    summary: ComputedValue
    columns: List[StageColumn]
    rows: List[ReportRow]


@dataclass
class Report:
    name: str
    datasheet_id: UUID
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
    datasheet_id: Optional[UUID]
    element_id: Optional[UUID]
    element_id: Optional[UUID]
