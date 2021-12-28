from uuid import UUID
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Union, Dict
from expert_dollup.shared.database_services import QueryFilter


@dataclass
class FormulaDependency:
    target_type_id: UUID
    name: str


@dataclass
class FormulaDependencyGraph:
    formulas: List[FormulaDependency]
    nodes: List[FormulaDependency]

    @property
    def dependencies(self) -> List[str]:
        dependencies_concat: List[str] = []

        for formula in self.formulas:
            dependencies_concat.append(formula.name)

        for node in self.nodes:
            dependencies_concat.append(node.name)

        return dependencies_concat


@dataclass
class AstNode:
    kind: str
    values: Dict[str, Union[str, bool, int, float]] = field(default_factory=dict)
    properties: Dict[str, "AstNode"] = field(default_factory=dict)
    children: Dict[str, List["AstNode"]] = field(default_factory=dict)

    def dict(self) -> dict:
        return asdict(self)


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
    final_ast: dict


@dataclass
class FormulaInstance:
    project_id: UUID
    formula_id: UUID
    node_id: UUID
    node_path: List[UUID]
    formula_name: str
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