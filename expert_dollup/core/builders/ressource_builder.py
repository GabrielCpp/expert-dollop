from uuid import UUID
from expert_dollup.infra.providers import WordProvider
from expert_dollup.core.domains import Ressource


class RessourceBuilder:
    def __init__(self, word_provider: WordProvider):
        self.word_provider = word_provider

    def build(self, ressource_id: UUID, owner_id: UUID, prefix: str) -> Ressource:
        separator = "_"
        middle = self.word_provider.pick_joined(3, separator)
        suffix = ressource_id.hex
        name = separator.join([prefix, middle, suffix])
        ressource = Ressource(id=ressource_id, name=name, owner_id=owner_id)
        return ressource
