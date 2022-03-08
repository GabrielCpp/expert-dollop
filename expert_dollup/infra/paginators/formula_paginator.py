from expert_dollup.shared.database_services import (
    CollectionPaginator,
    FieldTokenEncoder,
)
from expert_dollup.core.domains import Formula


class FormulaPaginator(CollectionPaginator[Formula]):
    class Meta:
        default_page_encoder = FieldTokenEncoder("name", str, str, "")
