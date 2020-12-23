
from predykt.infra.predykt_db import PredyktDatabase, project_container_table, ProjectContainerDao
from predykt.core.domains import ProjectContainer
from predykt.shared.database_services import BaseCrudTableService


class ProjectContainerService(BaseCrudTableService[ProjectContainer]):
    class Meta:
        table = project_container_table
        dao = ProjectContainerDao
        domain = ProjectContainer
        seach_filters = {}
