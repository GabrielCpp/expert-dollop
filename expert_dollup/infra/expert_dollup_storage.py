from pydantic import BaseModel
from uuid import UUID
from typing import Optional, Union, List
from .storage_connectors.storage_client import StorageClient


class ExpertDollupStorage(StorageClient):
    pass


class UnitInstanceDao(BaseModel):
    formula_id: Optional[UUID]
    node_id: UUID
    node_path: List[UUID]
    name: str
    calculation_details: str
    result: Union[str, bool, int, float]
