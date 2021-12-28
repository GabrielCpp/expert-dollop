from uuid import UUID
from typing import List
from expert_dollup.infra.expert_dollup_db import ProjectFormulaInstanceDao
from expert_dollup.core.domains import FormulaInstance
import gzip
import struct


def read_from(format, f):
    return struct.unpack(format, f.read(struct.calcsize(format)))[0]


class FormulaInstanceService:
    def __init__(self):
        pass

    async def load_instances(self, project_id: UUID):
        instances = []
        null_uuid = UUID(int=0)

        with gzip.open("./instances.jsonl.gzip", "rb") as f:
            instance_count = read_from("H", f)

            for _ in range(0, instance_count):
                formula_id = UUID(bytes=f.read(16))
                node_id = UUID(bytes=f.read(16))
                node_path = [
                    item
                    for item in (UUID(bytes=f.read(16)) for _ in range(0, 5))
                    if item != null_uuid
                ]

                formula_name_len = read_from("H", f)
                formula_name = f.read(formula_name_len).decode("utf8")

                calculation_details_len = read_from("L", f)
                calculation_details = f.read(calculation_details_len).decode("utf8")

                value_type = chr(read_from("B", f))

                if value_type == "I":
                    value = read_from("l", f)
                elif value_type == "F":
                    value = read_from("d", f)
                elif value_type == "B":
                    value = True if read_from("B", f) == 1 else False
                elif value_type == "S":
                    value_len = read_from("L", f)
                    value = f.read(value_len).decode("utf8")
                else:
                    raise Exception(f"Unkown value type {value_type}")

                instances.append(
                    FormulaInstance(
                        calculation_details=calculation_details,
                        formula_id=formula_id,
                        formula_name=formula_name,
                        node_id=node_id,
                        project_id=project_id,
                        result=value,
                        node_path=node_path,
                    )
                )

        return instances

    async def save_instances(self, project_id: UUID, instances: List[FormulaInstance]):
        null_uuid = UUID(int=0)

        with gzip.GzipFile("./instances.jsonl.gzip", compresslevel=9, mode="wb") as f:
            f.write(struct.pack("H", len(instances)))

            for instance in instances:
                f.write(instance.formula_id.bytes)
                f.write(instance.node_id.bytes)

                for index in range(0, 5):
                    uuid = (
                        instance.node_path[index]
                        if index < len(instance.node_path)
                        else null_uuid
                    )
                    f.write(uuid.bytes)

                f.write(struct.pack("H", len(instance.formula_name)))
                f.write(instance.formula_name.encode("utf8"))

                f.write(struct.pack("L", len(instance.calculation_details)))
                f.write(instance.calculation_details.encode("utf8"))

                if isinstance(instance.result, int):
                    f.write(struct.pack("B", ord("I")))
                    f.write(struct.pack("l", instance.result))
                elif isinstance(instance.result, float):
                    f.write(struct.pack("B", ord("F")))
                    f.write(struct.pack("d", instance.result))
                elif isinstance(instance.result, bool):
                    f.write(struct.pack("B", ord("B")))
                    f.write(struct.pack("B", 1 if instance.result else 0))
                elif isinstance(instance.result, str):
                    f.write(struct.pack("B", ord("S")))
                    f.write(struct.pack("L", len(instance.result)))
                    f.write(instance.result.encode("utf8"))
