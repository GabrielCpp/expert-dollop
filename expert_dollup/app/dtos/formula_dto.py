from uuid import UUID
from typing import List
from datetime import datetime
from expert_dollup.shared.starlette_injection import CamelModel


class FormulaExpressionDto(CamelModel):
    id: UUID
    project_definition_id: UUID
    attached_to_type_id: UUID
    name: str
    expression: str
    path: List[UUID]
    creation_date_utc: datetime


class InputFormulaDto(CamelModel):
    id: UUID
    project_definition_id: UUID
    path: List[UUID]
    name: str
    expression: str
