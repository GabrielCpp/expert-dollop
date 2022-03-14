from decimal import Decimal
from uuid import UUID
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Union
from expert_dollup.shared.database_services import QueryFilter
from .values_union import PrimitiveUnion


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
class AstNodeValue:
    number: Optional[Decimal] = None
    text: Optional[str] = None
    enabled: Optional[bool] = None


@dataclass
class AstNode:
    kind: str
    values: Dict[str, Union[AstNodeValue, str]] = field(default_factory=dict)
    properties: Dict[str, int] = field(default_factory=dict)
    children: Dict[str, List[int]] = field(default_factory=dict)


@dataclass
class FlatAst:
    nodes: List[AstNode]
    root_index: int

    def dict(self) -> dict:
        return asdict(self)


@dataclass
class FormulaExpression:
    id: UUID
    project_definition_id: UUID
    attached_to_type_id: UUID
    name: str
    expression: str


@dataclass
class Formula(FormulaExpression):
    dependency_graph: FormulaDependencyGraph

    @property
    def report_dict(self):
        return {
            "name": self.name,
            "expression": self.expression,
            "attached_to_type_id": self.attached_to_type_id,
        }


@dataclass
class StagedFormula(Formula):
    final_ast: dict


StagedFormulas = List[StagedFormula]


@dataclass
class StagedFormulasKey:
    project_definition_id: UUID


@dataclass
class UnitInstance:
    formula_id: Optional[UUID]
    node_id: UUID
    path: List[UUID]
    name: str
    calculation_details: str
    result: PrimitiveUnion

    @property
    def report_dict(self) -> dict:
        return asdict(self)


@dataclass
class UnitInstanceElement:
    project_id: UUID
    element_def_id: UUID
    formula_id: UUID
    node_id: UUID
    datasheet_element_reference: UUID


UnitInstanceCache = List[UnitInstance]


@dataclass
class UnitInstanceCacheKey:
    project_id: UUID


class FormulaFilter(QueryFilter):
    id: Optional[UUID]
    project_definition_id: Optional[UUID]
    attached_to_type_id: Optional[UUID]
    name: Optional[str]
    expression: Optional[str]


class FormulaPluckFilter(QueryFilter):
    ids: Optional[List[UUID]]
    names: Optional[List[str]]
    attached_to_type_ids: Optional[UUID]


class FormulaCachePluckFilter(QueryFilter):
    formula_ids: List[UUID]
