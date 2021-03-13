from typing import Awaitable
from uuid import UUID
from sqlalchemy import desc, select, and_
from sqlalchemy import func
from expert_dollup.shared.database_services import BaseCompositeCrudTableService, Page
from expert_dollup.core.domains import PaginatedRessource, DatasheetElement
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
        seach_filters = {}
        table_filter_type = DatasheetElementFilter

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

    async def find_datasheet_elements(
        self, paginated_ressource: PaginatedRessource[UUID]
    ) -> Awaitable[Page[DatasheetElement]]:
        offset = (
            0
            if paginated_ressource.next_page_token is None
            else int(paginated_ressource.next_page_token)
        )

        query = (
            self._table.select()
            .where(self._table.c.datasheet_id == paginated_ressource.query)
            .order_by(
                desc(self._table.c.creation_date_utc),
                desc(self._table.c.child_element_reference),
            )
            .limit(paginated_ressource.limit)
            .offset(paginated_ressource.limit * offset)
        )

        records = await self._database.fetch_all(query)
        results = self.map_many_to(records, self._dao, self._domain)

        return Page[DatasheetElement](
            next_page_token=str(offset + 1),
            limit=paginated_ressource.limit,
            results=results,
        )
