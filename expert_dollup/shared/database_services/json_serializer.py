from orjson import dumps, loads
import dataclasses
from typing import Any, Union
from uuid import UUID
from datetime import datetime, date
from pydantic import BaseModel
from decimal import Decimal


def default(obj):
    if isinstance(obj, UUID):
        return str(obj)

    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)

    if isinstance(obj, Decimal):
        return str(obj)

    if isinstance(obj, (date, datetime)):
        return obj.isoformat()

    if isinstance(obj, BaseModel):
        return obj.dict()

    raise TypeError()


class JsonSerializer:
    @staticmethod
    def encode(x: str) -> bytes:
        return dumps(x, default=default)

    @staticmethod
    def decode(x: Union[bytes, bytearray, memoryview, str]) -> Any:
        return loads(x)