from uuid import UUID
from expert_dollup.shared.modeling import CamelModel


class LabelCollectionDto(CamelModel):
    id: UUID
    datasheet_definition_id: UUID
    name: str
