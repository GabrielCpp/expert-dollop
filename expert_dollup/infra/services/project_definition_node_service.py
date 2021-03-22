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
from expert_dollup.infra.path_transform import join_uuid_path
from expert_dollup.infra.expert_dollup_db import (
    project_definition_node_table,
    ProjectDefinitionNodeDao,
    ExpertDollupDatabase,
)
from expert_dollup.shared.automapping import Mapper


class ProjectDefinitionNode2(BaseCrudTableService[ProjectDefinitionNode]):
    class Meta:
        table = project_definition_node_table
        dao = ProjectDefinitionNodeDao
        domain = ProjectDefinitionNode
        table_filter_type = ProjectDefinitionNodeFilter
        paginator = IdStampedDateCursorEncoder.for_fields("creation_date_utc", "name")


class ProjectDefinitionNodeService:
    def __init__(self, database: ExpertDollupDatabase, mapper: Mapper):
        self._node_crud = ProjectDefinitionNode2(database, mapper)

    async def find_by_id(self, id: UUID):
        return await self._node_crud.find_by_id(id)

    async def insert(self, domain):
        return await self._node_crud.insert(domain)

    async def insert_many(self, domains):
        return await self._node_crud.insert_many(domains)

    async def find_by(self, query_filter):
        return await self._node_crud.find_by(query_filter)

    async def find_by_paginated(self, query_filter, limit, next_page_token=None):
        return await self._node_crud.find_by_paginated(
            query_filter, limit, next_page_token
        )

    async def find_one_by(self, query_filter):
        return await self._node_crud.find_one_by(query_filter)

    async def delete_by_id(self, id: UUID):
        return await self._node_crud.delete_by_id(id)

    async def has_path(self, path: List[UUID]) -> Awaitable[bool]:
        if len(path) == 0:
            return True

        parent_id = path[-1]
        parent_path = join_uuid_path(path[0:-1])
        query = select([self._node_crud.table_id]).where(
            and_(
                self._node_crud._table.c.path == parent_path,
                self._node_crud._table.c.id == parent_id,
            )
        )
        value = await self._node_crud._database.fetch_one(query=query)

        return not value is None

    async def delete_child_of(self, id: UUID) -> Awaitable:
        value = await self._node_crud.find_by_id(id)
        path_to_delete = join_uuid_path(value.subpath)
        query = self._node_crud._table.delete().where(
            and_(
                self._node_crud._table.c.project_def_id == value.project_def_id,
                self._node_crud._table.c.mixed_paths.op("@>")([path_to_delete]),
            )
        )

        await self._node_crud._database.execute(query)

    async def find_children_tree(self, project_def_id: UUID, path: List[UUID]):
        path_filter = join_uuid_path(path)
        query = (
            select([self._node_crud._table])
            .where(
                and_(
                    self._node_crud._table.c.project_def_id == project_def_id,
                    self._node_crud._table.c.mixed_paths.op("@>")([path_filter]),
                )
            )
            .order_by(desc(func.length(self._node_crud._table.c.path)))
        )

        records = await self._node_crud._database.fetch_all(query=query)
        results = self._node_crud.map_many_to(
            records, self._node_crud._dao, self._node_crud._domain
        )
        return results

    async def find_viewable_layers(
        self,
        root_section_id: Optional[UUID],
        sub_root_section_id: Optional[UUID],
        form_id: Optional[UUID],
    ):
        pass