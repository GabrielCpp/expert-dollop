from typing import Awaitable, List, AsyncGenerator
from uuid import UUID
from sqlalchemy import select, text, bindparam, String, and_
from sqlalchemy.dialects.postgresql import ARRAY
from expert_dollup.infra.expert_dollup_db import project_definition_container_table, ProjectDefinitionContainerDao
from expert_dollup.core.domains import ProjectDefinitionContainer
from expert_dollup.shared.database_services import BaseCrudTableService
from sqlalchemy.dialects import postgresql

DELETE_BY_MIXED_PATH = text(
    f"DELETE FROM {project_definition_container_table.name} WHERE mixed_paths <@ :element")


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

    async def delete_child_of(self, id: UUID) -> Awaitable:
        query = self._table.select().where(self.table_id == id)
        value = await self._database.fetch_one(query=query)

        if value is None:
            return

        value = ProjectDefinitionContainerDao(**value)
        path_to_delete = '/'.join([*value.path, str(value.id)])
        sql = DELETE_BY_MIXED_PATH.bindparams(bindparam(
            key="element",
            value=[path_to_delete],
            type_=ARRAY(String, dimensions=1)
        ))

        await self._database.execute(sql)

    async def all_from_project(self, project_def_id: UUID) -> AsyncGenerator[ProjectDefinitionContainer, None]:
        query = self._table.select().where(self._table.c.project_def_id == project_def_id)
        return self.map_over(self._database.iterate(query))
