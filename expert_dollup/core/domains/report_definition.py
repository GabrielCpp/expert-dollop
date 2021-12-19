from dataclasses import dataclass
from uuid import UUID
from typing import List


@dataclass
class ReportJoin:
    from_object_name: str
    from_property_name: str
    join_on_collection: str
    join_on_attribute: str
    alias_name: str
    warn_about_idle_items: bool = True


@dataclass
class ReportInitialSelection:
    from_object_name: str
    alias_name: str


@dataclass
class ReportStructure:
    datasheet_selection_alias: str
    joins_cache: List[ReportJoin]


@dataclass
class ReportColumn:
    name: str
    expression: str
    is_top_level: bool = False


@dataclass
class ReportDefinition:
    id: UUID
    project_def_id: UUID
    name: str
    columns: List[ReportColumn]
    structure: ReportStructure
    group_by: List[str]
    order_by: List[str]
