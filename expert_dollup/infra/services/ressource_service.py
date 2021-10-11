from expert_dollup.infra.expert_dollup_db import (
    ressource_table,
    RessourceDao,
)
from expert_dollup.core.domains import Ressource
from expert_dollup.shared.database_services import PostgresTableService


class RessourceService(PostgresTableService[Ressource]):
    class Meta:
        table = ressource_table
        dao = RessourceDao
        domain = Ressource
        table_filter_type = None
