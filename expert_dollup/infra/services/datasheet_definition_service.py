from expert_dollup.shared.database_services import BaseCrudTableService
from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    datasheet_definition_table,
    DatasheetDefinitionDao,
)
from expert_dollup.core.domains import DatasheetDefinition


class DatasheetDefinitionService(BaseCrudTableService[DatasheetDefinition]):
    class Meta:
        table = datasheet_definition_table
        dao = DatasheetDefinitionDao
        domain = DatasheetDefinition
        table_filter_type = None
