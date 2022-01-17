from expert_dollup.shared.database_services import (
    CollectionPaginator,
    FieldTokenEncoder,
)
from expert_dollup.core.domains import Datasheet


class DatasheetPaginator(CollectionPaginator[Datasheet]):
    class Meta:
        default_page_encoder = FieldTokenEncoder("name", str, str, "")
