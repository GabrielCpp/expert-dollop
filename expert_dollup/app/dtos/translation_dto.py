from expert_dollup.shared.starlette_injection import CamelModel
from uuid import UUID
from datetime import datetime


class TranslationDto(CamelModel):
    id: UUID
    ressource_id: UUID
    locale: str
    scope: UUID
    name: str
    value: str
    creation_date_utc: datetime


class TranslationInputDto(CamelModel):
    id: UUID
    ressource_id: UUID
    locale: str
    scope: UUID
    name: str
    value: str


class TranslationIdDto(CamelModel):
    ressource_id: UUID
    locale: str
    scope: UUID
    name: str
