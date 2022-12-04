from expert_dollup.shared.starlette_injection import CamelModel
from uuid import UUID
from datetime import datetime


class TranslationDto(CamelModel):
    ressource_id: UUID
    locale: str
    scope: UUID
    name: str
    value: str
    creation_date_utc: datetime

    @property
    def id(self):
        return "_".join([str(self.ressource_id), self.locale, self.name])


class NewTranslationDto(CamelModel):
    locale: str
    name: str
    scope: UUID
    value: str


class FieldTranslationDto(CamelModel):
    locale: str
    name: str
    value: str
