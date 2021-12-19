from expert_dollup.shared.starlette_injection import CamelModel
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
