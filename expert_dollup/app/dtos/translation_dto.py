from expert_dollup.shared.modeling import CamelModel
from uuid import UUID
from datetime import datetime


class TranslationDto(CamelModel):
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
