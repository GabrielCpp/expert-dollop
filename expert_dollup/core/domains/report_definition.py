from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal
from typing import List, Dict, Union, Optional
from expert_dollup.shared.database_services import QueryFilter

ReportDefinitionColumnDict = Dict[
    str, Union[str, Decimal, bool, int, UUID, List[UUID], None]
]
ReportRowDict = Dict[str, ReportDefinitionColumnDict]
ReportRowsCache = List[ReportRowDict]


@dataclass
class ReportRowKey:
    project_definition_id: UUID
    report_definition_id: UUID


@dataclass
class ReportJoin:
    from_object_name: str
    from_property_name: str
    join_on_collection: str
    join_on_attribute: str
    alias_name: str
    warn_about_idle_items: bool = True
    same_cardinality: bool = False
    allow_dicard_element: bool = False


@dataclass
class AttributeBucket:
    bucket_name: str
    attribute_name: str

    def get(self, row: ReportRowDict):
        return row[self.bucket_name][self.attribute_name]


@dataclass
class ReportComputation:
    name: str
    expression: str
    unit: Union[str, AttributeBucket, None] = None
    is_visible: bool = True


@dataclass
class StageSummary:
    label: AttributeBucket
    summary: ReportComputation


@dataclass
class ReportStructure:
    datasheet_selection_alias: str
    formula_attribute: AttributeBucket
    datasheet_attribute: AttributeBucket
    joins_cache: List[ReportJoin]
    columns: List[ReportComputation]
    group_by: List[AttributeBucket]
    order_by: List[AttributeBucket]
    stage_summary: StageSummary
    report_summary: List[ReportComputation]


@dataclass
class ReportDefinition:
    id: UUID
    project_definition_id: UUID
    name: str
    structure: ReportStructure
    distributable: bool


class ReportDefinitionFilter(QueryFilter):
    project_definition_id: Optional[UUID]
    distributable: Optional[bool]
