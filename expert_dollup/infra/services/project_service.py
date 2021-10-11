from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    project_table,
    ProjectDao,
)
from expert_dollup.core.domains import ProjectDetails
from expert_dollup.shared.database_services import (
    TableService,
    IdStampedDateCursorEncoder,
)


class ProjectService(TableService[ProjectDetails]):
    class Meta:
        table = project_table
        dao = ProjectDao
        domain = ProjectDetails
        table_filter_type = None
        paginator = IdStampedDateCursorEncoder.for_fields("name", str, str, "")
