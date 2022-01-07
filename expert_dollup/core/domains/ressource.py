from dataclasses import dataclass
from uuid import UUID


@dataclass
class Ressource:
    id: UUID
    kind: str
    owner_id: UUID
