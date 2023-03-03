from pydantic import BaseModel, Field
from uuid import UUID
from typing import List
from datetime import datetime
from bson import encode, decode
from ..expert_dollup_db import PrimitiveWithNoneUnionDao


class UnitDao(BaseModel):
    class Meta:
        key_of = lambda obj: ""
        encode = encode
        decode = decode

    node_id: UUID
    path: List[UUID]
    name: str = Field(max_length=64)
    value: PrimitiveWithNoneUnionDao
    dependencies: List[str]
    calculation_details: str = ""
    computable: bool
    creation_date_utc: datetime
