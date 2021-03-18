from expert_dollup.shared.database_services import BaseCrudTableService
from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    datasheet_definition_label_table,
    LabelDao,
)
from expert_dollup.core.domains import Label


class LabelService(BaseCrudTableService[Label]):
    class Meta:
        table = datasheet_definition_label_table
        dao = LabelDao
        domain = Label
        table_filter_type = None
