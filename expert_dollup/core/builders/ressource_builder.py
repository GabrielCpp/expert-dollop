from uuid import UUID
from expert_dollup.infra.providers import WordProvider


class RessourceBuilder:
    def __init__(self, word_provider: WordProvider):
        self.word_provider = word_provider

    def build(self, ressource_id: UUID, prefix: str):
        middle = self.word_provider.pick_join(3)
        name = prefix + middle + suffix + ressource_id.hex
        ressource = Ressource(id=ressource_id, name=name, owner_id=uuid4())
