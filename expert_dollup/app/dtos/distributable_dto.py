from dataclasses import dataclass
from uuid import UUID
from typing import List, Dict
from enum import Enum
from datetime import datetime
from .report_dto import ComputedValueDto, ReportColumnDto
from expert_dollup.shared.starlette_injection import CamelModel

ColumnLabelDto = str


@dataclass
class DistributableItemDto(CamelModel):
    id: UUID
    distribution_ids: List[UUID]
    node_id: UUID
    formula_id: UUID
    element_def_id: UUID
    columns: Dict[ColumnLabelDto, ReportColumnDto]


@dataclass
class DistributableGroupDto(CamelModel):
    summary: ComputedValueDto
    items: List[DistributableItemDto]


class DistributionStateDto(Enum):
    PENDING = "PENDING"
    SEEN = "SEEN"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"


@dataclass
class DistributionDto(CamelModel):
    id: UUID
    file_url: str
    creation_date_utc: datetime
    item_ids: List[UUID]
    state: DistributionStateDto


@dataclass
class DistributableDto(CamelModel):
    project_id: UUID
    report_definition_id: UUID
    groups: List[DistributableGroupDto]
    distributions: List[DistributionDto]
