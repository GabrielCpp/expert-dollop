from uuid import UUID
from expert_dollup.shared.starlette_injection import CamelModel


class FormulaExpressionDto(CamelModel):
    id: UUID
    project_definition_id: UUID
    attached_to_type_id: UUID
    name: str
    expression: str


class InputFormulaDto(CamelModel):
    id: UUID
    project_definition_id: UUID
    attached_to_type_id: UUID
    name: str
    expression: str
