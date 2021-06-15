from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter


@dataclass
class Translation:
    id: UUID
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


class TranslationFilter(QueryFilter):
    id: Optional[UUID]
    ressource_id: Optional[UUID]
    locale: Optional[str]
    scope: Optional[UUID]
    name: Optional[str]
    value: Optional[str]
    creation_date_utc: Optional[datetime]