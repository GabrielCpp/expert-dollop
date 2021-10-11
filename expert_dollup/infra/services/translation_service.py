from expert_dollup.infra.expert_dollup_db import (
    translation_table,
    TranslationDao,
)
from expert_dollup.core.domains import (
    Translation,
    TranslationFilter,
    TranslationRessourceLocaleQuery,
)
from expert_dollup.shared.database_services import (
    TableService,
    IdStampedDateCursorEncoder,
    ExactMatchFilter,
)


class TranslationService(TableService[Translation]):
    class Meta:
        table = translation_table
        dao = TranslationDao
        domain = Translation
        table_filter_type = TranslationFilter
        paginator = IdStampedDateCursorEncoder.for_fields("id")
        custom_filters = {
            TranslationRessourceLocaleQuery: ExactMatchFilter(translation_table)
        }
