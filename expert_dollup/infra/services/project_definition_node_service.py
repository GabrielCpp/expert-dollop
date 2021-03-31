from typing import Awaitable, List, AsyncGenerator, Optional
from uuid import UUID
from sqlalchemy import select, String, and_, or_, desc
from sqlalchemy.sql.expression import func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects import postgresql
from expert_dollup.shared.database_services import (
    BaseCrudTableService,
    Page,
    IdStampedDateCursorEncoder,
)
from expert_dollup.core.domains import (
    ProjectDefinitionNode,
    ProjectDefinitionNodeFilter,
)
from expert_dollup.core.utils.path_transform import join_uuid_path
from expert_dollup.infra.expert_dollup_db import (
    project_definition_node_table,
    ProjectDefinitionNodeDao,
    ExpertDollupDatabase,
)
from expert_dollup.shared.automapping import Mapper


class ProjectDefinitionNodeService(BaseCrudTableService[ProjectDefinitionNode]):
    class Meta:
        table = project_definition_node_table
        dao = ProjectDefinitionNodeDao
        domain = ProjectDefinitionNode
        table_filter_type = ProjectDefinitionNodeFilter
        paginator = IdStampedDateCursorEncoder.for_fields("creation_date_utc", "name")

    async def has_path(self, path: List[UUID]) -> Awaitable[bool]:
        if len(path) == 0:
            return True

        parent_id = path[-1]
        parent_path = join_uuid_path(path[0:-1])
        query = select([self.table_id]).where(
            and_(
                self._table.c.path == parent_path,
                self._table.c.id == parent_id,
            )
        )
        value = await self._database.fetch_one(query=query)

        return not value is None

    async def delete_child_of(self, id: UUID) -> Awaitable:
        value = await self.find_by_id(id)
        path_to_delete = join_uuid_path(value.subpath)
        query = self._table.delete().where(
            and_(
                self._table.c.project_def_id == value.project_def_id,
                self._table.c.path.like(f"{path_to_delete}%"),
            )
        )

        await self._database.execute(query)

    async def find_children_tree(
        self, project_def_id: UUID, path: List[UUID]
    ) -> Awaitable[List[ProjectDefinitionNode]]:
        path_filter = join_uuid_path(path)
        query = (
            select([self._table])
            .where(
                and_(
                    self._table.c.project_def_id == project_def_id,
                    self._table.c.path.like(f"{path_filter}%"),
                )
            )
            .order_by(desc(self._table.c.level))
        )

        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)
        return results

    async def find_root_sections(
        self, project_def_id: UUID
    ) -> Awaitable[List[ProjectDefinitionNode]]:
        query = (
            select([self._table])
            .where(
                and_(
                    self._table.c.project_def_id == project_def_id,
                    self._table.c.path == "",
                )
            )
            .order_by(desc(self._table.c.level))
        )

        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)
        return results

    async def find_root_section_containers(
        self, project_def_id: UUID, root_section_id: UUID
    ) -> Awaitable[List[ProjectDefinitionNode]]:
        query = (
            select([self._table])
            .where(
                and_(
                    self._table.c.project_def_id == project_def_id,
                    self._table.c.display_query_internal_id == root_section_id,
                )
            )
            .order_by(desc(self._table.c.level))
        )

        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)
        return results

    async def find_form_content(
        self, project_def_id: UUID, form_id: UUID
    ) -> Awaitable[List[ProjectDefinitionNode]]:
        query = (
            select([self._table])
            .where(
                and_(
                    self._table.c.project_def_id == project_def_id,
                    self._table.c.display_query_internal_id == form_id,
                )
            )
            .order_by(desc(self._table.c.level))
        )

        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)

        return results