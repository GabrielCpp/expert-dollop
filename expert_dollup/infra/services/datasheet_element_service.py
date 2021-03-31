from typing import Awaitable, Optional, Tuple
from datetime import datetime
from uuid import UUID
from sqlalchemy import desc, select, and_
from sqlalchemy import func
from expert_dollup.shared.database_services import (
    BaseCompositeCrudTableService,
    Page,
    IdStampedDateCursorEncoder,
)
from expert_dollup.core.domains import DatasheetElement
from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    datasheet_element_table,
    DatasheetElementDao,
)
from expert_dollup.core.domains import DatasheetElement, DatasheetElementFilter


class DatasheetElementService(BaseCompositeCrudTableService[DatasheetElement]):
    class Meta:
        table = datasheet_element_table
        dao = DatasheetElementDao
        domain = DatasheetElement
        table_filter_type = DatasheetElementFilter
        paginator = IdStampedDateCursorEncoder.for_fields("child_element_reference")

    async def get_collection_size(self, datasheet_id, element_def_id):
        query = (
            select([func.count()])
            .select_from(self._table)
            .where(
                and_(
                    self._table.c.datasheet_id == datasheet_id,
                    self._table.c.element_def_id == element_def_id,
                )
            )
        )

        count = await self._database.fetch_val(query)
        return count
