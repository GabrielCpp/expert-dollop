from expert_dollup.shared.database_services import BaseCrudTableService
from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    datasheet_definition_element_table,
    DatasheetDefinitionElementDao,
)
from expert_dollup.core.domains import DatasheetDefinitionElement


class DatasheetDefinitionElementService(
    BaseCrudTableService[DatasheetDefinitionElement]
):
    class Meta:
        table = datasheet_definition_element_table
        dao = DatasheetDefinitionElementDao
        domain = DatasheetDefinitionElement
        table_filter_type = None
