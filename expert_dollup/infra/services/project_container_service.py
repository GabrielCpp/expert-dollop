from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    project_container_table,
    ProjectContainerDao,
)
from expert_dollup.core.domains import ProjectContainer
from expert_dollup.shared.database_services import BaseCrudTableService


class ProjectContainerService(BaseCrudTableService[ProjectContainer]):
    class Meta:
        table = project_container_table
        dao = ProjectContainerDao
        domain = ProjectContainer
        seach_filters = {}
