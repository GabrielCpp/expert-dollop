from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal
from typing import List, Dict, Union, Optional
from expert_dollup.shared.database_services import QueryFilter

ReportColumnDict = Dict[str, Union[str, Decimal, bool, int, UUID, List[UUID], None]]
ReportRowDict = Dict[str, ReportColumnDict]
ReportRowsCache = List[ReportRowDict]


@dataclass
class ReportRowKey:
    project_def_id: UUID
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
    expression: str
    unit_id: Optional[str] = None


@dataclass
class ReportColumn:
    name: str
    expression: str
    unit_id: Optional[str] = None
    unit: Optional[AttributeBucket] = None
    is_visible: bool = True


@dataclass
class StageGrouping:
    label: AttributeBucket
    summary: ReportComputation


@dataclass
class ReportStructure:
    datasheet_selection_alias: str
    formula_attribute: AttributeBucket
    datasheet_attribute: AttributeBucket
    joins_cache: List[ReportJoin]
    columns: List[ReportColumn]
    group_by: List[AttributeBucket]
    order_by: List[AttributeBucket]
    stage: StageGrouping


@dataclass
class ReportDefinition:
    id: UUID
    project_def_id: UUID
    name: str
    structure: ReportStructure


class ReportDefinitionFilter(QueryFilter):
    project_def_id: UUID