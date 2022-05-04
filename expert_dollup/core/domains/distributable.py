from dataclasses import dataclass
from uuid import UUID
from typing import List, Dict
from enum import Enum
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter
from .report import ComputedValue, ReportColumn

ColumnLabel = str


@dataclass
class DistributableItem:
    distribution_ids: List[UUID]
    node_id: UUID
    formula_id: UUID
    element_def_id: UUID
    columns: Dict[ColumnLabel, ReportColumn]

    @property
    def id(self) -> str:
        return ".".join(
            [self.node_id.hex, self.formula_id.hex, self.element_def_id.hex]
        )


@dataclass
class DistributableGroup:
    summary: ComputedValue
    items: List[DistributableItem]


class DistributionState(Enum):
    PENDING = "PENDING"
    SEEN = "SEEN"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"


@dataclass
class Distribution:
    id: UUID
    file_url: str
    creation_date_utc: datetime
    item_ids: List[UUID]
    state: DistributionState


@dataclass
class Distributable:
    project_id: UUID
    report_definition_id: UUID
    groups: List[DistributableGroup]
    distributions: List[Distribution]


@dataclass
class DistributableId(QueryFilter):
    project_id: UUID
    report_definition_id: UUID