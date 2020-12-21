from predykt.infra.predykt_db import PredyktDatabase, ressource_table, RessourceDao
from predykt.core.domains import Ressource
from predykt.shared.database_services import BaseCrudTableService


class RessourceService(BaseCrudTableService[Ressource]):
    class Meta:
        table = ressource_table
        dao = RessourceDao
        domain = Ressource
        seach_filters = {}
