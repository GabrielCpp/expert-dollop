from uuid import UUID
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union
from ast import AST


@dataclass
class Formula:
    id: UUID
    project_def_id: UUID
    attached_to_type_id: UUID
    name: str
    expression: str
    generated_ast: Optional[AST]


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
    container_id: UUID
    generation_tag: UUID
    calculation_details: str
    result: Union[str, bool, int, float]


@dataclass
class FieldNode:
    id: UUID
    name: str
    path: List[UUID]
    expression: Union[str, int, float, bool]


@dataclass
class FormulaNode:
    id: UUID
    name: str
    path: List[UUID]
    expression: AST
    formula_id: UUID
    dependencies: List[str]
