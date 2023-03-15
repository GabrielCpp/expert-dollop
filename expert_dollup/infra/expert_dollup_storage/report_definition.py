from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime
from bson import encode, decode
from expert_dollup.infra.daos import *


class CompiledReportDao(BaseModel):
    class Meta:
        key_of = (
            lambda obj: f"project_definitions/{obj.project_definition_id}/reports/{obj.id}"
        )
        encode = encode
        decode = decode

    key: CompiledReportKeyDao
    name: str
    structure: ReportStructureDao
    rows: List[ReportRowDictDao]
