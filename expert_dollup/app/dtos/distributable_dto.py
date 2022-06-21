from dataclasses import dataclass
from uuid import UUID
from typing import List, Dict
from enum import Enum
from datetime import datetime
from .report_dto import ComputedValueDto, ReportColumnDto
from expert_dollup.shared.starlette_injection import CamelModel


class SuppliedItemDto(CamelModel):
    datasheet_id: UUID
    element_def_id: UUID
    child_reference_id: UUID
    organisation_id: UUID


class DistributableItemDto(CamelModel):
    project_id: UUID
    report_definition_id: UUID
    node_id: UUID
    formula_id: UUID
    supplied_item: SuppliedItemDto
    distribution_ids: List[UUID]

    summary: ComputedValueDto
    columns: List[ComputedValueDto]
    obsolete: bool
    creation_date_utc: datetime


class DistributionStateDto(Enum):
    PENDING = "PENDING"
    SEEN = "SEEN"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"


@dataclass
class DistributionDto(CamelModel):
    id: UUID
    file_url: str
    item_ids: List[UUID]
    state: DistributionStateDto
    obsolete: bool
    creation_date_utc: datetime
