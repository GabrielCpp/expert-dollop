from dataclasses import dataclass
from uuid import UUID
from typing import List, Dict, Union

ReportRowDict = Dict[str, Dict[str, Union[str, float, bool, int, None]]]


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
class ReportColumn:
    name: str
    expression: str
    is_visible: bool = True


@dataclass
class AttributeBucket:
    bucket_name: str
    attribute_name: str

    def get(self, row: ReportRowDict):
        return row[self.bucket_name][self.attribute_name]


@dataclass
class ReportStructure:
    datasheet_selection_alias: str
    formula_attribute: AttributeBucket
    datasheet_attribute: AttributeBucket
    joins_cache: List[ReportJoin]
    columns: List[ReportColumn]
    group_by: List[AttributeBucket]
    order_by: List[AttributeBucket]


@dataclass
class ReportDefinition:
    id: UUID
    project_def_id: UUID
    name: str
    structure: ReportStructure
