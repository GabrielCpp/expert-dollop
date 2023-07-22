from pydantic import BaseModel
from typing import List, Union
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing_extensions import TypeAlias


class IntFieldValueDao(BaseModel):
    integer: int


class DecimalFieldValueDao(BaseModel):
    numeric: Decimal


class StringFieldValueDao(BaseModel):
    text: str


class BoolFieldValueDao(BaseModel):
    enabled: bool


class ReferenceIdDao(BaseModel):
    uuid: UUID


PrimitiveWithNoneUnionDao: TypeAlias = Union[
    BoolFieldValueDao, IntFieldValueDao, StringFieldValueDao, DecimalFieldValueDao, None
]

PrimitiveUnionDao: TypeAlias = Union[
    BoolFieldValueDao, IntFieldValueDao, StringFieldValueDao, DecimalFieldValueDao
]

PrimitiveWithReferenceDaoUnion = Union[
    BoolFieldValueDao,
    IntFieldValueDao,
    StringFieldValueDao,
    DecimalFieldValueDao,
    ReferenceIdDao,
]
