from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    project_table,
    ProjectDao,
)
from expert_dollup.core.domains import Project
from expert_dollup.shared.database_services import BaseCrudTableService


class ProjectService(BaseCrudTableService[Project]):
    class Meta:
        table = project_table
        dao = ProjectDao
        domain = Project
        seach_filters = {}
