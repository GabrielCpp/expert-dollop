from expert_dollup.shared.database_services import (
    PostgresTableService,
    IdStampedDateCursorEncoder,
)
from expert_dollup.infra.expert_dollup_db import (
    datasheet_definition_table,
    DatasheetDefinitionDao,
)
from expert_dollup.core.domains import DatasheetDefinition


class DatasheetDefinitionService(PostgresTableService[DatasheetDefinition]):
    class Meta:
        table = datasheet_definition_table
        dao = DatasheetDefinitionDao
        domain = DatasheetDefinition
        table_filter_type = None
        paginator = IdStampedDateCursorEncoder.for_fields("name", str, str, "")
