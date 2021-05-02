from typing import Awaitable, List
from uuid import UUID
from sqlalchemy import select, join, and_, desc, or_
from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    project_container_meta_table,
    ProjectContainerMetaDao,
)
from expert_dollup.core.domains import ProjectContainerMeta, ProjectContainerMetaFilter
from expert_dollup.shared.database_services import BaseCompositeCrudTableService


class ProjectContainerMetaService(BaseCompositeCrudTableService[ProjectContainerMeta]):
    class Meta:
        table = project_container_meta_table
        dao = ProjectContainerMetaDao
        domain = ProjectContainerMeta
        table_filter_type = ProjectContainerMetaFilter

    async def find_root_sections(
        self, project_id: UUID
    ) -> Awaitable[List[ProjectContainerMeta]]:
        query = select([self._table]).where(
            and_(
                self._table.c.project_id == project_id,
                self._table.c.display_query_internal_id == project_id,
            )
        )

        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)
        return sorted(results, key=lambda x: len(x.definition.path))

    async def find_root_section_containers(
        self, project_id: UUID, root_section_def_id: UUID
    ) -> Awaitable[List[ProjectContainerMeta]]:
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
    ) -> Awaitable[List[ProjectContainerMeta]]:
        query = select([self._table]).where(
            and_(
                self._table.c.project_id == project_id,
                self._table.c.display_query_internal_id == form_def_id,
            )
        )

        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)

        return sorted(results, key=lambda x: len(x.definition.path))
