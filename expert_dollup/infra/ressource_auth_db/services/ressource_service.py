from expert_dollup.core.domains import Ressource
from expert_dollup.shared.database_services import CollectionServiceProxy
from ..daos import RessourceDao


class RessourceService(CollectionServiceProxy[Ressource]):
    class Meta:
        dao = RessourceDao
        domain = Ressource
