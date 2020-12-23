from predykt.infra.predykt_db import PredyktDatabase, translation_table, TranslationDao
from predykt.core.domains import Translation, TranslationRessourceLocaleQuery
from predykt.shared.database_services import BaseCompositeCrudTableService, AndColumnFilter


class TranslationService(BaseCompositeCrudTableService[Translation]):
    class Meta:
        table = translation_table
        dao = TranslationDao
        domain = Translation
        seach_filters = {
            TranslationRessourceLocaleQuery: AndColumnFilter([
                (translation_table.c.ressource_id, lambda f: f.ressource_id),
                (translation_table.c.locale, lambda f: f.locale),
            ])
        }
