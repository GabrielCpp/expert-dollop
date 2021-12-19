from expert_dollup.shared.modeling import CamelModel
from uuid import UUID


class IntFieldValueDto(CamelModel):
    integer: int


class DecimalFieldValueDto(CamelModel):
    numeric: float


class StringFieldValueDto(CamelModel):
    text: str


class BoolFieldValueDto(CamelModel):
    enabled: bool


class ReferenceIdDto(CamelModel):
    uuid: UUID
