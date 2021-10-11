from expert_dollup.shared.database_services import (
    TableService,
    IdStampedDateCursorEncoder,
)
from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    datasheet_definition_element_table,
    DatasheetDefinitionElementDao,
)
from expert_dollup.core.domains import DatasheetDefinitionElement


class DatasheetDefinitionElementService(TableService[DatasheetDefinitionElement]):
    class Meta:
        table = datasheet_definition_element_table
        dao = DatasheetDefinitionElementDao
        domain = DatasheetDefinitionElement
        table_filter_type = None
        paginator = IdStampedDateCursorEncoder.for_fields("name", str, str, "")
