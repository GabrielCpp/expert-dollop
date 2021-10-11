from uuid import UUID
from dataclasses import dataclass
from typing import List, Dict, Optional, Union
from ast import AST
from expert_dollup.shared.database_services import QueryFilter


@dataclass
class Formula:
    id: UUID
    project_def_id: UUID
    attached_to_type_id: UUID
    name: str
    expression: str


@dataclass
class FormulaDetails:
    formula: Formula
    formula_dependencies: Dict[str, UUID]
    field_dependencies: Dict[str, UUID]
    formula_ast: AST


@dataclass
class FormulaCachedResult:
    project_id: UUID
    formula_id: UUID
    node_id: UUID
    calculation_details: str
    result: Union[str, bool, int, float]


@dataclass
class FieldNode:
    id: UUID
    name: str
    path: List[UUID]
    type_id: UUID
    type_path: List[UUID]
    expression: Union[str, int, float, bool]


@dataclass
class FormulaNode:
    id: UUID
    name: str
    path: List[UUID]
    type_id: UUID
    type_path: List[UUID]
    expression: AST
    formula_id: UUID
    dependencies: List[str]


class FormulaFilter(QueryFilter):
    id: Optional[UUID]
    project_def_id: Optional[UUID]
    attached_to_type_id: Optional[UUID]
    name: Optional[str]
    expression: Optional[str]
