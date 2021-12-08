from expert_dollup.shared.database_services import CollectionServiceProxy
from expert_dollup.infra.expert_dollup_db import LabelCollectionDao
from expert_dollup.core.domains import LabelCollection


class LabelCollectionService(CollectionServiceProxy[LabelCollection]):
    class Meta:
        dao = LabelCollectionDao
        domain = LabelCollection
        table_filter_type = None
