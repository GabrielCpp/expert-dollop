from hashlib import md5
from uuid import UUID


def make_uuid(value: str) -> UUID:
    return UUID(bytes=md5(value.encode("utf8")).digest())
