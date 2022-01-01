from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from .expert_dollup_db import PrimitiveUnionDao
from .storage_connectors.storage_client import StorageClient


class ExpertDollupStorage(StorageClient):
    pass


class UnitInstanceDao(BaseModel):
    formula_id: Optional[UUID]
    node_id: UUID
    node_path: List[UUID]
    name: str
    calculation_details: str
    result: PrimitiveUnionDao
