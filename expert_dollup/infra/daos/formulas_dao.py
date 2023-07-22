from pydantic import BaseModel, Field
from typing import List
from uuid import UUID
from datetime import datetime


class FormulaDependencyDao(BaseModel):
    target_type_id: UUID
    name: str = Field(max_length=64)


class FormulaDependencyGraphDao(BaseModel):
    formulas: List[FormulaDependencyDao]
    nodes: List[FormulaDependencyDao]


class StagedFormulaDao(BaseModel):
    id: UUID
    project_definition_id: UUID
    attached_to_type_id: UUID
    name: str = Field(max_length=64)
    expression: str
    final_ast: dict
    dependency_graph: FormulaDependencyGraphDao
