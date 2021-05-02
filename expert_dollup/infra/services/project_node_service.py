import jsonpickle
from typing import List, Optional, Awaitable, Any, Dict
from uuid import UUID
from sqlalchemy import select, join, and_, desc, or_
from expert_dollup.core.domains import (
    ProjectNode,
    ProjectNodeTreeNode,
    ProjectNodeMeta,
    ProjectDefinitionNode,
    ProjectNodeTree,
    ProjectNodeFilter,
    FieldNode,
)
from expert_dollup.shared.database_services import BaseCrudTableService
from expert_dollup.core.utils.path_transform import join_uuid_path, split_uuid_path
from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    project_node_table,
    ProjectNodeDao,
    project_definition_node_table,
    ProjectDefinitionNodeDao,
    project_node_meta_table,
    ProjectNodeMetaDao,
)


class ProjectNodeService(BaseCrudTableService[ProjectNode]):
    class Meta:
        table = project_node_table
        dao = ProjectNodeDao
        domain = ProjectNode
        table_filter_type = ProjectNodeFilter

    async def find_children(
        self, project_id: UUID, path: List[UUID], level: Optional[int] = None
    ) -> Awaitable[ProjectNode]:
        path_filter = join_uuid_path(path)
        other_filters = []

        if not level is None:
            other_filters.append(self._table.c.level == level)

        query = (
            select([self._table])
            .where(
                and_(
                    self._table.c.project_id == project_id,
                    self._table.c.path.like(f"{path_filter}%"),
                    *other_filters,
                )
            )
            .order_by(desc(self._table.c.level))
        )

        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)
        return results

    async def remove_collection(self, container: ProjectNode) -> Awaitable:
        path_to_delete = join_uuid_path(container.subpath)
        query = self._table.delete().where(
            and_(
                self._table.c.project_id == container.project_id,
                self._table.c.path.like(f"{path_to_delete}%"),
            )
        )
        await self._database.execute(query=query)

    async def find_root_sections(
        self, project_id: UUID
    ) -> Awaitable[List[ProjectDefinitionNode]]:
        query = (
            select([self._table])
            .where(
                and_(
                    self._table.c.project_id == project_id,
                    self._table.c.display_query_internal_id == project_id,
                )
            )
            .order_by(desc(self._table.c.level))
        )

        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)
        return results

    async def find_root_section_nodes(
        self, project_id: UUID, root_section_def_id: UUID
    ) -> Awaitable[List[ProjectDefinitionNode]]:
        query = (
            select([self._table])
            .where(
                and_(
                    self._table.c.project_id == project_id,
                    self._table.c.display_query_internal_id == root_section_def_id,
                )
            )
            .order_by(desc(self._table.c.level))
        )

        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)
        return results

    async def find_form_content(
        self, project_id: UUID, form_def_id: UUID
    ) -> Awaitable[List[ProjectDefinitionNode]]:
        query = (
            select([self._table])
            .where(
                and_(
                    self._table.c.project_id == project_id,
                    self._table.c.display_query_internal_id == form_def_id,
                )
            )
            .order_by(desc(self._table.c.level))
        )

        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)

        return results

    async def get_all_fields(self, project_id: UUID) -> Awaitable[List[FieldNode]]:
        join_definition = self._table.join(
            project_definition_node_table,
            project_definition_node_table.c.id == self._table.c.type_id,
        )

        query = (
            select(
                [
                    project_definition_node_table.c.name,
                    project_definition_node_table.c.id,
                    project_definition_node_table.c.path,
                    self._table.c.value,
                ]
            )
            .select_from(join_definition)
            .where(
                and_(
                    self._table.c.project_id == project_id,
                    self._table.c.value.isnot(None),
                )
            )
        )

        records = await self._database.fetch_all(query=query)

        return [
            FieldNode(
                id=record.get("id"),
                name=record.get("name"),
                path=split_uuid_path(record.get("path")),
                expression=jsonpickle.decode(record.get("value")),
            )
            for record in records
        ]
