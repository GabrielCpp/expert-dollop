from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    project_definition_table,
    ProjectDefinitionDao,
)
from expert_dollup.core.domains import ProjectDefinition
from expert_dollup.shared.database_services import BaseCrudTableService


class ProjectDefinitionService(BaseCrudTableService[ProjectDefinition]):
    class Meta:
        table = project_definition_table
        dao = ProjectDefinitionDao
        domain = ProjectDefinition
        table_filter_type = None
