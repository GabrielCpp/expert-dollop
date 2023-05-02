from pydantic import BaseModel
from typing import List
from uuid import UUID
from bson import encode, decode
from expert_dollup.infra.daos import *


class FormulaPackDao(BaseModel):
    class Meta:
        key_of = lambda obj: f"project_definitions/{obj}/formulas"
        encode = encode
        decode = decode

    key: UUID
    formulas: List[StagedFormulaDao]
