from predykt.shared.modeling import CamelModel
from uuid import UUID


class TranslationDto(CamelModel):
    ressource_id: UUID
    locale: str
    name: str
    value: str


class TranslationIdDto(CamelModel):
    ressource_id: UUID
    locale: str
    name: str
