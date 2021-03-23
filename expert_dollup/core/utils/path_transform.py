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


def list_uuid_to_str(ls: List[UUID]) -> List[str]:
    return [str(item) for item in ls]


def list_str_to_uuid(ls: List[str]) -> List[UUID]:
    return [UUID(item) for item in ls]


def build_path_steps(path: List[UUID]) -> List[str]:
    str_path = [str(item) for item in path]
    mixed_path: List[str] = []

    if len(str_path) > 0:
        mixed_path.append(join_path(str_path))

    for upper_index in range(1, len(str_path)):
        mixed_path.append(join_path(str_path[0:upper_index]))

    return mixed_path
