from expert_dollup.infra.expert_dollup_db import RessourceDao
from expert_dollup.core.domains import Ressource
from expert_dollup.shared.database_services import CollectionServiceProxy


class RessourceService(CollectionServiceProxy[Ressource]):
    class Meta:
        dao = RessourceDao
        domain = Ressource
