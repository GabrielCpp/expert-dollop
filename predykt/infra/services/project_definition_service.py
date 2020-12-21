from predykt.infra.predykt_db import PredyktDatabase, project_definition_table, ProjectDefinitionDao
from predykt.core.domains import ProjectDefinition
from predykt.shared.database_services import BaseCrudTableService


class ProjectDefinitionService(BaseCrudTableService[ProjectDefinition]):
    class Meta:
        table = project_definition_table
        dao = ProjectDefinitionDao
        domain = ProjectDefinition
        seach_filters = {}
