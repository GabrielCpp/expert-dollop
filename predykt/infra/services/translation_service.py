from predykt.infra.predykt_db import PredyktDatabase, translation_table, TranslationDao
from predykt.core.domains import Translation
from predykt.shared.database_services import BaseCrudTableService


class TranslationService(BaseCrudTableService[Translation]):
    class Meta:
        table = translation_table
        dao = TranslationDao
        domain = Translation
        seach_filters = {}
