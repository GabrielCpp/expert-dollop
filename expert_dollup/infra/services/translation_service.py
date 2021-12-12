from expert_dollup.infra.expert_dollup_db import TranslationDao
from expert_dollup.core.domains import (
    Translation,
    TranslationFilter,
    TranslationRessourceLocaleQuery,
)
from expert_dollup.shared.database_services import (
    CollectionServiceProxy,
    IdStampedDateCursorEncoder,
)


class TranslationService(CollectionServiceProxy[Translation]):
    class Meta:
        dao = TranslationDao
        domain = Translation
        table_filter_type = TranslationFilter
        paginator = IdStampedDateCursorEncoder.for_fields("id")
