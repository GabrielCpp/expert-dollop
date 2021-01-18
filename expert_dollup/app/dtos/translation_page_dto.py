from expert_dollup.shared.modeling import CamelModel
from typing import List, Generic
from .translation_dto import TranslationDto


class TranslationPageDto(CamelModel):
    next_page_token: str
    limit: int
    results: List[TranslationDto]