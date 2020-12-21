from predykt.infra.predykt_db import PredyktDatabase, project_table, ProjectDao
from predykt.core.domains import Project
from predykt.shared.database_services import BaseCrudTableService


class ProjectService(BaseCrudTableService[Project]):
    class Meta:
        table = project_table
        dao = ProjectDao
        domain = Project
        seach_filters = {}
