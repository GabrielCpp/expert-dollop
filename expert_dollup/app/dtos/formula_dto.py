from uuid import UUID
from expert_dollup.shared.modeling import CamelModel


class FormulaDto(CamelModel):
    id: UUID
    project_def_id: UUID
    attached_to_type_id: UUID
    name: str
    expression: str
    generated_ast: str
