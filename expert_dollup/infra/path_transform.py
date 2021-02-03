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


def build_path_steps(path: List[UUID]) -> List[str]:
    mixed_path: List[str] = []
    str_path = [str(item) for item in path]

    for upper_index in range(2, len(str_path)):
        mixed_path.append(join_path(str_path[0:upper_index]))

    return mixed_path
