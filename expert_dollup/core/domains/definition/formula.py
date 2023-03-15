from decimal import Decimal
from uuid import UUID
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Optional, Dict, Union, Callable
from expert_dollup.shared.database_services import (
    QueryFilter,
    queries,
    Pluck,
    PluckSubRessource,
)
from ..values_union import PrimitiveWithNoneUnion


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
class FormulaExpression:
    id: UUID
    project_definition_id: UUID
    attached_to_type_id: UUID
    name: str
    expression: str
    path: List[UUID]
    creation_date_utc: datetime


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

    @staticmethod
    def from_formula(
        formula: Formula, compile_to_dict: Callable[[str], dict]
    ) -> "StagedFormula":
        return StagedFormula(
            id=formula.id,
            project_definition_id=formula.project_definition_id,
            attached_to_type_id=formula.attached_to_type_id,
            name=formula.name,
            expression=formula.expression,
            dependency_graph=formula.dependency_graph,
            final_ast=compile_to_dict(formula.expression),
            path=formula.path,
            creation_date_utc=formula.creation_date_utc,
        )


@dataclass
class FormulaPack:
    key: UUID
    formulas: List[StagedFormula]


@dataclass
class UnitElement:
    project_id: UUID
    aggregate_id: UUID
    formula_id: UUID
    node_id: UUID
    datasheet_element_reference: UUID


class FormulaFilter(QueryFilter):
    id: Optional[UUID]
    project_definition_id: Optional[UUID]
    attached_to_type_id: Optional[UUID]
    name: Optional[str]
    expression: Optional[str]


@queries.register_child_of(Pluck)
@queries.register_child_of(PluckSubRessource)
class FormulaPluckFilter(FormulaFilter):
    ids: Optional[List[UUID]]
    names: Optional[List[str]]
    attached_to_type_ids: Optional[UUID]
