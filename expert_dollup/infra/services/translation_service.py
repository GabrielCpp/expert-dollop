from expert_dollup.infra.expert_dollup_db import (
    translation_table,
    TranslationDao,
)
from expert_dollup.core.domains import Translation, TranslationFilter
from expert_dollup.shared.database_services import (
    BaseCompositeCrudTableService,
    IdStampedDateCursorEncoder,
)


class TranslationService(BaseCompositeCrudTableService[Translation]):
    class Meta:
        table = translation_table
        dao = TranslationDao
        domain = Translation
        table_filter_type = TranslationFilter
        paginator = IdStampedDateCursorEncoder.for_fields("id")
