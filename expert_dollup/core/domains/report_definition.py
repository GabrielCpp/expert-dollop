from dataclasses import dataclass
from uuid import UUID
from typing import List


@dataclass
class ReportJoin:
    from_object_name: str
    from_property_name: str
    to_object_name: str
    to_property_name: str
    alias_name: str
    is_inner_join: bool = True


@dataclass
class ReportInitialSelection:
    from_object_name: str
    from_property_name: str
    alias_name: str
    distinct: bool


@dataclass
class ReportStructure:
    initial_selection: ReportInitialSelection
    joins_cache: List[ReportJoin]
    joins: List[ReportJoin]


@dataclass
class ReportColumn:
    name: str
    expression: str


@dataclass
class ReportDefinition:
    id: UUID
    project_def_id: UUID
    name: str
    columns: List[ReportColumn]
    structure: ReportStructure
    group_by: List[str]
    order_by: List[str]
