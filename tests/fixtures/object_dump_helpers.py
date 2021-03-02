import json
import os
from uuid import UUID

dump_file_path = "."
index = 0


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)

        return json.JSONEncoder.default(self, obj)


def set_dump_path(path: str) -> None:
    dump_file_path = dump_file_path


def dump_to_file(json_serializable):
    global index

    path = os.path.join(dump_file_path, f"{index}.txt")
    index = index + 1

    with open(path, "w") as outfile:
        json.dump(json_serializable, outfile, indent=2, sort_keys=True, cls=UUIDEncoder)


def dump_snapshot(json_serializable) -> str:
    return json.dumps(json_serializable, indent=2, sort_keys=True, cls=UUIDEncoder)


def jsonify(v):
    return json.dumps(v, indent=2, sort_keys=True, cls=UUIDEncoder)
