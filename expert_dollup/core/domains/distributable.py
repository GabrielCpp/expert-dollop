from dataclasses import dataclass
from uuid import UUID
from typing import List
from enum import Enum
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter
from .report import ComputedValue

ColumnLabel = str


@dataclass
class SuppliedItem:
    datasheet_id: UUID
    element_def_id: UUID
    child_reference_id: UUID
    organization_id: UUID


@dataclass
class DistributableItem:
    project_id: UUID
    report_definition_id: UUID
    node_id: UUID
    formula_id: UUID
    supplied_item: SuppliedItem
    distribution_ids: List[UUID]

    summary: ComputedValue
    columns: List[ComputedValue]
    obsolete: bool
    creation_date_utc: datetime

    @property
    def id(self) -> str:
        return ".".join(
            [
                self.node_id.hex,
                self.formula_id.hex,
                self.supplied_item.element_def_id.hex,
            ]
        )


@dataclass
class DistributableUpdate:
    items: List[DistributableItem]
    obsolete_distribution_ids: List[UUID]


class DistributionState(Enum):
    PENDING = "PENDING"
    SEEN = "SEEN"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"


@dataclass
class Distribution:
    id: UUID
    file_url: str
    item_ids: List[str]
    state: DistributionState
    obsolete: bool
    creation_date_utc: datetime


class DistributableItemFilter(QueryFilter):
    project_id: UUID
    report_definition_id: UUID
