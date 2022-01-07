import json
import os
import dataclasses
import datetime
from uuid import UUID
from decimal import Decimal
from pydantic.main import BaseModel
from enum import Enum

dump_file_path = "."
index = 0


class ExtraEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)

        if isinstance(obj, BaseModel):
            return obj.dict()

        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)

        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()

        if isinstance(obj, Decimal):
            return str(obj)

        if issubclass(type(obj), Enum):
            return str(obj)

        return json.JSONEncoder.default(self, obj)


def set_dump_path(path: str) -> None:
    global dump_file_path
    dump_file_path = dump_file_path


def dump_to_file(json_serializable):
    global index

    path = os.path.join(dump_file_path, f"{index}.txt")
    index = index + 1

    with open(path, "w") as outfile:
        json.dump(
            json_serializable, outfile, indent=2, sort_keys=True, cls=ExtraEncoder
        )
        outfile.flush()
        os.fsync(outfile)


def dump_snapshot(json_serializable) -> str:
    return json.dumps(json_serializable, indent=2, sort_keys=True, cls=ExtraEncoder)


def jsonify(v):
    return json.dumps(v, indent=2, sort_keys=True, cls=ExtraEncoder)
