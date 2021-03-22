from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class Translation:
    ressource_id: UUID
    locale: str
    scope: UUID
    name: str
    value: str
    creation_date_utc: datetime


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
