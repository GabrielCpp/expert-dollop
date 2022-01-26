from expert_dollup.shared.database_services import (
    CollectionPaginator,
    FieldTokenEncoder,
)
from expert_dollup.core.domains import Translation


class TranslationPaginator(CollectionPaginator[Translation]):
    class Meta:
        default_page_encoder = FieldTokenEncoder("id")
