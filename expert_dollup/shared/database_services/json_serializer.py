import json
import dataclasses
from typing import Any
from uuid import UUID
from datetime import datetime, date
from pydantic import BaseModel


class ExtraEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)

        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)

        if isinstance(obj, (date, datetime)):
            return obj.isoformat()

        if isinstance(obj, BaseModel):
            return obj.dict()

        return json.JSONEncoder.default(self, obj)


class JsonSerializer:
    @staticmethod
    def encode(x: str, indent=2) -> str:
        return json.dumps(x, indent=indent, sort_keys=True, cls=ExtraEncoder)

    @staticmethod
    def decode(x: str) -> Any:
        return json.loads(x)