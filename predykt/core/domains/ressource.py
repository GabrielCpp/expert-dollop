from dataclasses import dataclass
from uuid import UUID


@dataclass
class Ressource:
    id: UUID
    name: str
    owner_id: UUID
