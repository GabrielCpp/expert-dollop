from dataclasses import dataclass
from uuid import UUID
from typing import Dict, Union, Optional
from expert_dollup.shared.database_services import QueryFilter
from .report_definition import ReportRowDict


@dataclass
class ReportDefinitionRowCache:
    report_def_id: UUID
    row_digest: str
    row: ReportRowDict


class ReportCacheFilter(QueryFilter):
    report_def_id: Optional[UUID]