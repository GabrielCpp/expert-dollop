from expert_dollup.shared.database_services import BaseCompositeCrudTableService
from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    datasheet_element_table,
    DatasheetElementDao,
)
from expert_dollup.core.domains import DatasheetElement


class DatasheetElementService(BaseCompositeCrudTableService[DatasheetElement]):
    class Meta:
        table = datasheet_element_table
        dao = DatasheetElementDao
        domain = DatasheetElement
        seach_filters = {}
        table_filter_type = None
