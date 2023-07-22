from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal
from typing import List, Dict, Union, Optional
from expert_dollup.shared.database_services import QueryFilter

ReportDefinitionColumnDict = Dict[str, Union[str, Decimal, bool, int, UUID, None]]
ReportRowDict = Dict[str, ReportDefinitionColumnDict]


@dataclass
class Expression:
    name: str
    flat_ast: Optional[dict] = None


@dataclass
class AttributeBucket:
    bucket_name: str
    attribute_name: str

    def get(self, row: ReportRowDict):
        return row[self.bucket_name][self.attribute_name]


@dataclass
class ReportComputation:
    name: str
    expression: Expression
    label: Optional[AttributeBucket] = None
    unit: Union[str, AttributeBucket, None] = None
    is_visible: bool = True


@dataclass
class ReportJoin:
    from_object: AttributeBucket
    on_object: AttributeBucket
    alias: str


@dataclass
class Selection:
    from_collection_id: UUID
    from_alias: str
    joins_cache: List[ReportJoin]
    formula_attribute: AttributeBucket
    datasheet_attribute: AttributeBucket


@dataclass
class ReportStructure:
    selection: Selection
    columns: List[ReportComputation]
    group_by: List[AttributeBucket]
    having: Optional[Expression]
    order_by: List[AttributeBucket]
    stage_summary: ReportComputation
    report_summary: List[ReportComputation]


@dataclass
class ReportDefinition:
    id: UUID
    project_definition_id: UUID
    name: str
    structure: ReportStructure
    distributable: bool


@dataclass
class CompiledReportKey:
    id: UUID
    project_definition_id: UUID


@dataclass
class CompiledReport:
    key: CompiledReportKey
    name: str
    structure: ReportStructure
    rows: List[ReportRowDict]


class ReportDefinitionFilter(QueryFilter):
    project_definition_id: Optional[UUID]
    distributable: Optional[bool]
