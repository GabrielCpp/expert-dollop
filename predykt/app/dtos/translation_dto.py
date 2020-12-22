from pydantic import BaseModel
from uuid import UUID


class TranslationDto(BaseModel):
    ressource_id: UUID
    locale: str
    name: str
    value: str


class TranslationIdDto(BaseModel):
    ressource_id: UUID
    locale: str
    name: str
