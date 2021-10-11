from expert_dollup.infra.expert_dollup_db import (
    project_definition_table,
    ProjectDefinitionDao,
)
from expert_dollup.core.domains import ProjectDefinition
from expert_dollup.shared.database_services import (
    PostgresTableService,
    IdStampedDateCursorEncoder,
)


class ProjectDefinitionService(PostgresTableService[ProjectDefinition]):
    class Meta:
        table = project_definition_table
        dao = ProjectDefinitionDao
        domain = ProjectDefinition
        table_filter_type = None
        paginator = IdStampedDateCursorEncoder.for_fields("name", str, str, "")
