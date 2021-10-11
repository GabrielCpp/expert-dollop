from typing import Awaitable, Optional, Tuple
from datetime import datetime
from uuid import UUID
from sqlalchemy import desc, select, and_
from sqlalchemy import func
from expert_dollup.shared.database_services import (
    ExactMatchFilter,
    PostgresTableService,
    IdStampedDateCursorEncoder,
)
from expert_dollup.core.domains import DatasheetElement
from expert_dollup.infra.expert_dollup_db import (
    datasheet_element_table,
    DatasheetElementDao,
)
from expert_dollup.core.domains import (
    DatasheetElement,
    DatasheetElementFilter,
    DatasheetElementId,
)


class DatasheetElementService(PostgresTableService[DatasheetElement]):
    class Meta:
        table = datasheet_element_table
        dao = DatasheetElementDao
        domain = DatasheetElement
        table_filter_type = DatasheetElementFilter
        paginator = IdStampedDateCursorEncoder.for_fields("child_element_reference")
        custom_filters = {DatasheetElementId: ExactMatchFilter(datasheet_element_table)}
