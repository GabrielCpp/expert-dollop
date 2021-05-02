from typing import Awaitable, List
from uuid import UUID
from sqlalchemy import select, join, and_, desc, or_
from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    project_node_meta_table,
    ProjectNodeMetaDao,
)
from expert_dollup.core.domains import ProjectNodeMeta, ProjectNodeMetaFilter
from expert_dollup.shared.database_services import BaseCompositeCrudTableService


class ProjectNodeMetaService(BaseCompositeCrudTableService[ProjectNodeMeta]):
    class Meta:
        table = project_node_meta_table
        dao = ProjectNodeMetaDao
        domain = ProjectNodeMeta
        table_filter_type = ProjectNodeMetaFilter

    async def find_root_sections(
        self, project_id: UUID
    ) -> Awaitable[List[ProjectNodeMeta]]:
        query = select([self._table]).where(
            and_(
                self._table.c.project_id == project_id,
                self._table.c.display_query_internal_id == project_id,
            )
        )

        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)
        return sorted(results, key=lambda x: len(x.definition.path))

    async def find_root_section_nodes(
        self, project_id: UUID, root_section_def_id: UUID
    ) -> Awaitable[List[ProjectNodeMeta]]:
        query = select([self._table]).where(
            and_(
                self._table.c.project_id == project_id,
                self._table.c.display_query_internal_id == root_section_def_id,
            )
        )

        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)
        return sorted(results, key=lambda x: len(x.definition.path))

    async def find_form_content(
        self, project_id: UUID, form_def_id: UUID
    ) -> Awaitable[List[ProjectNodeMeta]]:
        query = select([self._table]).where(
            and_(
                self._table.c.project_id == project_id,
                self._table.c.display_query_internal_id == form_def_id,
            )
        )

        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)

        return sorted(results, key=lambda x: len(x.definition.path))
