from dataclasses import dataclass
from uuid import UUID


@dataclass
class Translation:
    ressource_id: UUID
    locale: str
    name: str
    value: str


@dataclass
class TranslationId:
    ressource_id: UUID
    locale: str
    name: str
