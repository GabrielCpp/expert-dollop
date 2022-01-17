from expert_dollup.infra.expert_dollup_db import TranslationDao
from expert_dollup.core.domains import Translation
from expert_dollup.shared.database_services import CollectionServiceProxy


class TranslationService(CollectionServiceProxy[Translation]):
    class Meta:
        dao = TranslationDao
        domain = Translation
