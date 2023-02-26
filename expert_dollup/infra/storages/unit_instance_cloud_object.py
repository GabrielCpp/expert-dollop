from uuid import UUID
from typing import Optional
import gzip
import struct
from decimal import Decimal
from io import BytesIO
from expert_dollup.infra.expert_dollup_storage import ExpertDollupStorage
from expert_dollup.core.object_storage import ObjectStorage
from expert_dollup.core.domains import (
    Unit,
    UnitCacheKey,
    UnitCache,
)


def read_from(format, f):
    return struct.unpack(format, f.read(struct.calcsize(format)))[0]


class UnitCloudObject(ObjectStorage[UnitCache, UnitCacheKey]):
    def __init__(self, storage: ExpertDollupStorage):
        self.storage = storage

    async def load(self, ctx: UnitCacheKey) -> UnitCache:
        instances = []
        null_uuid = UUID(int=0)
        path = self.get_url(ctx)
        initial_bytes = await self.storage.download_binary(path)
        inbytes = BytesIO(initial_bytes)

        with gzip.GzipFile(fileobj=inbytes, mode="rb") as f:
            instance_count = read_from("H", f)

            for _ in range(0, instance_count):
                formula_id: Optional[UUID] = UUID(bytes=f.read(16))
                if formula_id == null_uuid:
                    formula_id = None

                node_id = UUID(bytes=f.read(16))
                node_path = [
                    item
                    for item in (UUID(bytes=f.read(16)) for _ in range(0, 5))
                    if item != null_uuid
                ]

                name_len = read_from("H", f)
                name = f.read(name_len).decode("utf8")

                if formula_id is None:
                    calculation_details = ""
                else:
                    calculation_details_len = read_from("L", f)
                    calculation_details = f.read(calculation_details_len).decode("utf8")

                value_type = chr(read_from("B", f))

                if value_type == "I":
                    value = read_from("l", f)
                elif value_type == "D":
                    value_len = read_from("L", f)
                    value = Decimal(f.read(value_len).decode("utf8"))
                elif value_type == "B":
                    value = True if read_from("B", f) == 1 else False
                elif value_type == "S":
                    value_len = read_from("L", f)
                    value = f.read(value_len).decode("utf8")
                else:
                    raise Exception(f"Unkown value type {value_type}")

                instances.append(
                    Unit(
                        calculation_details=calculation_details,
                        formula_id=formula_id,
                        name=name,
                        node_id=node_id,
                        result=value,
                        path=node_path,
                    )
                )

        return instances

    async def save(self, ctx: UnitCacheKey, instances: UnitCache):
        null_uuid = UUID(int=0)
        outbytes = BytesIO()

        with gzip.GzipFile(fileobj=outbytes, compresslevel=9, mode="wb") as f:
            f.write(struct.pack("H", len(instances)))

            for instance in instances:
                f.write((instance.formula_id or null_uuid).bytes)
                f.write(instance.node_id.bytes)

                for index in range(0, 5):
                    uuid = (
                        instance.path[index]
                        if index < len(instance.path)
                        else null_uuid
                    )

                    f.write(uuid.bytes)

                name = instance.name.encode("utf8")
                f.write(struct.pack("H", len(name)))
                f.write(name)

                if not instance.formula_id is None:
                    calculation_details = instance.calculation_details.encode("utf8")
                    f.write(struct.pack("L", len(calculation_details)))
                    f.write(calculation_details)

                if isinstance(instance.result, int):
                    f.write(struct.pack("B", ord("I")))
                    f.write(struct.pack("l", instance.result))
                elif isinstance(instance.result, Decimal):
                    f.write(struct.pack("B", ord("D")))
                    result = str(instance.result).encode("utf8")
                    f.write(struct.pack("L", len(result)))
                    f.write(result)
                elif isinstance(instance.result, bool):
                    f.write(struct.pack("B", ord("B")))
                    f.write(struct.pack("B", 1 if instance.result else 0))
                elif isinstance(instance.result, str):
                    result = instance.result.encode("utf8")
                    f.write(struct.pack("B", ord("S")))
                    f.write(struct.pack("L", len(result)))
                    f.write(result)

        outbytes.seek(0)
        output_bytes = outbytes.read()
        path = self.get_url(ctx)
        await self.storage.upload_binary(path, output_bytes)

    def get_url(self, ctx: UnitCacheKey) -> str:
        return f"projects/{ctx.project_id}/formula_instance.raw.gzip"
