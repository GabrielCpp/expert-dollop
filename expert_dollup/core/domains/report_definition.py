from dataclasses import dataclass
from uuid import UUID
from typing import List
from enum import Enum


class JoinType(Enum):
    AGGREGATE = "AGGREGATE"
    PROPERTY = "PROPERTY"
    TABLE_PROPERTY = "PROPERTY"


@dataclass
class ReportJoin:
    to_object_name: str
    from_object_name: str
    join_on_property_name: str
    join_type: JoinType


@dataclass
class ReportStructure:
    initial_selection: ReportJoin
    joins: List[ReportJoin]


@dataclass
class ReportColumn:
    id: UUID
    name: str
    expression: str


@dataclass
class ReportDefinition:
    id: UUID
    project_def_id: UUID
    name: str
    columns: List[ReportColumn]
    structure: ReportStructure
