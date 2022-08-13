from expert_dollup.shared.database_services import CollectionServiceProxy
from expert_dollup.infra.expert_dollup_db import DistributableItemDao
from expert_dollup.core.domains import DistributableItem


class DistributableItemService(CollectionServiceProxy[DistributableItem]):
    class Meta:
        dao = DistributableItemDao
        domain = DistributableItem
