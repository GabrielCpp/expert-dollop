from expert_dollup.shared.starlette_injection import CamelModel
from typing import Union
from uuid import UUID
from decimal import Decimal


class IntFieldValueDto(CamelModel):
    integer: int


class DecimalFieldValueDto(CamelModel):
    numeric: Decimal


class StringFieldValueDto(CamelModel):
    text: str


class BoolFieldValueDto(CamelModel):
    enabled: bool


class ReferenceIdDto(CamelModel):
    uuid: UUID


PrimitiveWithNoneUnionDto = Union[
    BoolFieldValueDto, IntFieldValueDto, StringFieldValueDto, DecimalFieldValueDto, None
]

PrimitiveUnionDto = Union[
    BoolFieldValueDto, IntFieldValueDto, StringFieldValueDto, DecimalFieldValueDto
]

PrimitiveWithReferenceUnionDto = Union[
    BoolFieldValueDto,
    IntFieldValueDto,
    StringFieldValueDto,
    DecimalFieldValueDto,
    ReferenceIdDto,
]

JsonSchemaDto = dict