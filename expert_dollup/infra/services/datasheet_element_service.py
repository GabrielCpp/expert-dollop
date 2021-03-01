from expert_dollup.shared.database_services import BaseCrudTableService
from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    datasheet_element_table,
    DatasheetElementDao,
)
from expert_dollup.core.domains import DatasheetElement


class DatasheetElementService(BaseCrudTableService[DatasheetElement]):
    class Meta:
        table = datasheet_element_table
        dao = DatasheetElementDao
        domain = DatasheetElement
        seach_filters = {}
        table_filter_type = None
