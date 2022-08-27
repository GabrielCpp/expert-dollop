from typing import DefaultDict, Protocol, Dict, List
from collections import defaultdict
from uuid import UUID, uuid4


def create_id_dict() -> DefaultDict[UUID, UUID]:
    return defaultdict(uuid4)


class ObjectWithId(Protocol):
    id: UUID


def map_id_to_object(objects: List[ObjectWithId]) -> Dict[UUID, ObjectWithId]:
    return {obj.id: obj for obj in objects}
