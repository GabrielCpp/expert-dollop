from expert_dollup.shared.database_services import (
    PostgresTableService,
    IdStampedDateCursorEncoder,
)
from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    datasheet_table,
    DatasheetDao,
)
from expert_dollup.core.domains import Datasheet, DatasheetFilter


class DatasheetService(PostgresTableService[Datasheet]):
    class Meta:
        table = datasheet_table
        dao = DatasheetDao
        domain = Datasheet
        table_filter_type = DatasheetFilter
        paginator = IdStampedDateCursorEncoder.for_fields("name", str, str, "")
