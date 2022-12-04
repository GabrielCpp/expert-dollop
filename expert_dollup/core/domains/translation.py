from dataclasses import dataclass
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter


@dataclass
class Translation:
    ressource_id: UUID
    locale: str
    scope: UUID
    name: str
    value: str
    creation_date_utc: datetime


@dataclass
class NewTranslation:
    locale: str
    name: str
    scope: UUID
    value: str


@dataclass
class FieldTranslation:
    locale: str
    name: str
    value: str


@dataclass
class TranslationId:
    ressource_id: UUID
    locale: str
    name: str


class TranslationFilter(QueryFilter):
    ressource_id: Optional[UUID]
    locale: Optional[str]
    scope: Optional[UUID]
    name: Optional[str]
    value: Optional[str]
    creation_date_utc: Optional[datetime]


class TranslationPluckFilter(QueryFilter):
    scopes: Optional[List[UUID]]
