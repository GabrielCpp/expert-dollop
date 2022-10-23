from typing import DefaultDict, Protocol, Dict, List, Protocol, Iterable
from collections import defaultdict
from uuid import UUID, uuid4


def create_id_dict() -> DefaultDict[UUID, UUID]:
    return defaultdict(uuid4)


class ObjectWithId(Protocol):
    id: UUID


def map_id_to_object(objects: List[ObjectWithId]) -> Dict[UUID, ObjectWithId]:
    return {obj.id: obj for obj in objects}


class NameProtocol(Protocol):
    name: str


def by_names(items: Iterable[NameProtocol]) -> Dict[str, NameProtocol]:
    return {item.name: item for item in items}


class IdProtocol(Protocol):
    id: UUID


def by_ids(items: Iterable[IdProtocol]) -> Dict[UUID, NameProtocol]:
    return {item.id: item for item in items}
