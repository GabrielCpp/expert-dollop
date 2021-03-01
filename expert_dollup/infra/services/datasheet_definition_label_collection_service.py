from expert_dollup.shared.database_services import BaseCrudTableService
from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    datasheet_definition_label_collection_table,
    LabelCollectionDao,
)
from expert_dollup.core.domains import LabelCollection


class LabelCollectionService(BaseCrudTableService[LabelCollection]):
    class Meta:
        table = datasheet_definition_label_collection_table
        dao = LabelCollectionDao
        domain = LabelCollection
        seach_filters = {}
        table_filter_type = None
