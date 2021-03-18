from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    translation_table,
    TranslationDao,
)
from expert_dollup.core.domains import Translation, TranslationRessourceLocaleQuery
from expert_dollup.shared.database_services import (
    BaseCompositeCrudTableService,
    IdStampedDateCursorEncoder,
)


class TranslationService(BaseCompositeCrudTableService[Translation]):
    class Meta:
        table = translation_table
        dao = TranslationDao
        domain = Translation
        table_filter_type = None
        paginator = IdStampedDateCursorEncoder.for_fields("creation_date_utc", "name")
