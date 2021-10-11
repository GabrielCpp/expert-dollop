from expert_dollup.shared.database_services import PostgresTableService
from expert_dollup.infra.expert_dollup_db import (
    datasheet_definition_label_table,
    LabelDao,
)
from expert_dollup.core.domains import Label


class LabelService(PostgresTableService[Label]):
    class Meta:
        table = datasheet_definition_label_table
        dao = LabelDao
        domain = Label
        table_filter_type = None
