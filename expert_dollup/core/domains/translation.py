from dataclasses import dataclass
from uuid import UUID


@dataclass
class Translation:
    ressource_id: UUID
    locale: str
    scope: UUID
    name: str
    value: str


@dataclass
class TranslationId:
    ressource_id: UUID
    locale: str
    scope: UUID
    name: str


@dataclass
class TranslationRessourceLocaleQuery:
    ressource_id: UUID
    locale: str
