from typing import Awaitable, List
from uuid import UUID
from sqlalchemy import select
from predykt.infra.predykt_db import project_definition_container_table, ProjectDefinitionContainerDao
from predykt.core.domains import ProjectDefinitionContainer
from predykt.shared.database_services import BaseCrudTableService


class ProjectDefinitionContainerService(BaseCrudTableService[ProjectDefinitionContainer]):
    class Meta:
        table = project_definition_container_table
        dao = ProjectDefinitionContainerDao
        domain = ProjectDefinitionContainer
        seach_filters = {}

    async def has_path(self, path: List[UUID]) -> Awaitable[bool]:
        if len(path) == 0:
            return True

        path_str = [str(element) for element in path]
        query = select([self.table_id]).where(self._table.c.path == path_str)
        value = await self._database.fetch_one(query=query)

        return not value is None
