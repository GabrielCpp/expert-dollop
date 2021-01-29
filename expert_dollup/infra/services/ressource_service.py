from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    ressource_table,
    RessourceDao,
)
from expert_dollup.core.domains import Ressource
from expert_dollup.shared.database_services import BaseCrudTableService


class RessourceService(BaseCrudTableService[Ressource]):
    class Meta:
        table = ressource_table
        dao = RessourceDao
        domain = Ressource
        seach_filters = {}
        table_filter_type = None
