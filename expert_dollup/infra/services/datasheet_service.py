from expert_dollup.shared.database_services import BaseCrudTableService
from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    datasheet_table,
    DatasheetDao,
)
from expert_dollup.core.domains import Datasheet


class DatasheetService(BaseCrudTableService[Datasheet]):
    class Meta:
        table = datasheet_table
        dao = DatasheetDao
        domain = Datasheet
        seach_filters = {}
        table_filter_type = None
