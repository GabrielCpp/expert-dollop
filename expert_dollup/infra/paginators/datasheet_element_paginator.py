from expert_dollup.shared.database_services import (
    CollectionPaginator,
    FieldTokenEncoder,
)
from expert_dollup.core.domains import DatasheetElement


class DatasheetElementPaginator(CollectionPaginator[DatasheetElement]):
    class Meta:
        default_page_encoder = FieldTokenEncoder("child_element_reference")
