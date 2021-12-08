from expert_dollup.infra.expert_dollup_db import ProjectDefinitionDao
from expert_dollup.core.domains import ProjectDefinition
from expert_dollup.shared.database_services import (
    CollectionServiceProxy,
    IdStampedDateCursorEncoder,
)


class ProjectDefinitionService(CollectionServiceProxy[ProjectDefinition]):
    class Meta:
        dao = ProjectDefinitionDao
        domain = ProjectDefinition
        table_filter_type = None
        paginator = IdStampedDateCursorEncoder.for_fields("name", str, str, "")
