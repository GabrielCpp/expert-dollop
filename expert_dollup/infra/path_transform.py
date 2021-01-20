from typing import List
from uuid import UUID


def join_path(path: List[str]) -> str:
    return "/".join(path)


def split_path(path: str) -> List[str]:
    if path == "":
        return []

    return path.split("/")


def split_uuid_path(path: str) -> List[UUID]:
    if path == "":
        return []

    return [UUID(item) for item in path.split("/")]


def join_uuid_path(path: List[UUID]) -> str:
    return "/".join([str(item) for item in path])
