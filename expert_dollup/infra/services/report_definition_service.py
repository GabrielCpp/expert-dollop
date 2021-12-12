from expert_dollup.infra.expert_dollup_db import ReportDefinitionDao
from expert_dollup.core.domains import ReportDefinition
from expert_dollup.shared.database_services import (
    CollectionServiceProxy,
    IdStampedDateCursorEncoder,
)


class ReportDefinitionService(CollectionServiceProxy[ReportDefinition]):
    class Meta:
        dao = ReportDefinitionDao
        domain = ReportDefinition
        paginator = IdStampedDateCursorEncoder.for_fields("name", str, str, "")