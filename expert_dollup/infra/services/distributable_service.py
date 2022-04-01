from expert_dollup.shared.database_services import CollectionServiceProxy
from expert_dollup.infra.expert_dollup_db import DistributableDao
from expert_dollup.core.domains import Distributable


class DistributableService(CollectionServiceProxy[Distributable]):
    class Meta:
        dao = DistributableDao
        domain = Distributable
