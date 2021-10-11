from expert_dollup.shared.database_services import PostgresTableService
from expert_dollup.infra.expert_dollup_db import (
    datasheet_definition_label_collection_table,
    LabelCollectionDao,
)
from expert_dollup.core.domains import LabelCollection


class LabelCollectionService(PostgresTableService[LabelCollection]):
    class Meta:
        table = datasheet_definition_label_collection_table
        dao = LabelCollectionDao
        domain = LabelCollection
        table_filter_type = None
