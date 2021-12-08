from expert_dollup.shared.database_services import (
    CollectionServiceProxy,
    IdStampedDateCursorEncoder,
)
from expert_dollup.infra.expert_dollup_db import DatasheetDao
from expert_dollup.core.domains import Datasheet, DatasheetFilter


class DatasheetService(CollectionServiceProxy[Datasheet]):
    class Meta:
        dao = DatasheetDao
        domain = Datasheet
        table_filter_type = DatasheetFilter
        paginator = IdStampedDateCursorEncoder.for_fields("name", str, str, "")
