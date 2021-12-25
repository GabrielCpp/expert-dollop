from uuid import UUID
from dataclasses import dataclass, asdict
from typing import List, Optional, Union
from ast import AST
from expert_dollup.shared.database_services import QueryFilter
from .project_node import ProjectNode


@dataclass
class FormulaDependency:
    target_type_id: UUID
    name: str


@dataclass
class FormulaDependencyGraph:
    formulas: List[FormulaDependency]
    nodes: List[FormulaDependency]


@dataclass
class FormulaExpression:
    id: UUID
    project_def_id: UUID
    attached_to_type_id: UUID
    name: str
    expression: str


@dataclass
class Formula(FormulaExpression):
    dependency_graph: FormulaDependencyGraph


@dataclass
class FormulaInstance:
    project_id: UUID
    formula_id: UUID
    node_id: UUID
    calculation_details: str
    result: Union[str, bool, int, float]

    @property
    def report_dict(self) -> dict:
        return asdict(self)


@dataclass
class FieldNode:
    id: UUID
    name: str
    path: List[UUID]
    type_id: UUID
    type_path: List[UUID]
    expression: Union[str, int, float, bool]


@dataclass
class ComputedFormula:
    formula: Formula
    result: FormulaInstance
    node: ProjectNode
    final_ast: AST


class FormulaFilter(QueryFilter):
    id: Optional[UUID]
    project_def_id: Optional[UUID]
    attached_to_type_id: Optional[UUID]
    name: Optional[str]
    expression: Optional[str]


class FormulaPluckFilter(QueryFilter):
    ids: Optional[List[UUID]]
    names: Optional[List[str]]
    attached_to_type_ids: Optional[UUID]


class FormulaInstanceFilter(QueryFilter):
    project_id: UUID


class FormulaCachePluckFilter(QueryFilter):
    formula_ids: List[UUID]