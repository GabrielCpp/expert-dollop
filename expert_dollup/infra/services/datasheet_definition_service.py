from expert_dollup.shared.database_services import (
    CollectionServiceProxy,
    IdStampedDateCursorEncoder,
)
from expert_dollup.infra.expert_dollup_db import DatasheetDefinitionDao
from expert_dollup.core.domains import DatasheetDefinition


class DatasheetDefinitionService(CollectionServiceProxy[DatasheetDefinition]):
    class Meta:
        dao = DatasheetDefinitionDao
        domain = DatasheetDefinition
        table_filter_type = None
        paginator = IdStampedDateCursorEncoder.for_fields("name", str, str, "")
