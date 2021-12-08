from expert_dollup.shared.database_services import (
    CollectionServiceProxy,
    IdStampedDateCursorEncoder,
)
from expert_dollup.core.domains import DatasheetElement
from expert_dollup.infra.expert_dollup_db import DatasheetElementDao
from expert_dollup.core.domains import (
    DatasheetElement,
    DatasheetElementFilter,
    DatasheetElementId,
)


class DatasheetElementService(CollectionServiceProxy[DatasheetElement]):
    class Meta:
        dao = DatasheetElementDao
        domain = DatasheetElement
        table_filter_type = DatasheetElementFilter
        paginator = IdStampedDateCursorEncoder.for_fields("child_element_reference")
        custom_filters = {DatasheetElementId}
