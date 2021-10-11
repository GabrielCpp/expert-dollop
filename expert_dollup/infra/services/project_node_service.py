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
from expert_dollup.core.domains.project_definition_node import (
    ProjectDefinitionNodeFilter,
)
from expert_dollup.shared.database_services import PostgresTableService
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


class ProjectNodeService(PostgresTableService[ProjectNode]):
    class Meta:
        table = project_node_table
        dao = ProjectNodeDao
        domain = ProjectNode
        table_filter_type = ProjectNodeFilter

    async def find_children(
        self, project_id: UUID, path: List[UUID], level: Optional[int] = None
    ) -> Awaitable[ProjectNode]:
        builder = (
            self.get_builder()
            .find_by(ProjectNodeFilter(project_id=project_id))
            .startwiths(ProjectNodeFilter(path=path))
        )

        if not level is None:
            builder.find_by(ProjectNodeFilter(level=level))

        builder.finalize()
        results = await self.find_by(builder, order_by=("level", "desc"))

        return results

    async def remove_collection(self, container: ProjectNode) -> Awaitable:
        builder = (
            self.get_builder()
            .find_by(ProjectNodeFilter(project_id=container.project_id))
            .startwiths(ProjectNodeFilter(path=container.subpath))
            .finalize()
        )

        await self.delete_by(builder)

    async def find_root_sections(
        self, project_id: UUID
    ) -> Awaitable[List[ProjectDefinitionNode]]:
        builder = (
            self.get_builder()
            .find_by(
                ProjectNodeFilter(
                    project_id=project_id, display_query_internal_id=project_id
                )
            )
            .finalize()
        )
        results = await self.find_by(builder, order_by=("level", "desc"))
        return results

    async def find_root_section_nodes(
        self, project_id: UUID, root_section_id: UUID
    ) -> Awaitable[List[ProjectDefinitionNode]]:
        builder = (
            self.get_builder()
            .find_by(
                ProjectNodeFilter(
                    project_id=project_id, display_query_internal_id=root_section_id
                )
            )
            .finalize()
        )
        results = await self.find_by(builder, order_by=("level", "desc"))
        return results

    async def find_form_content(
        self, project_id: UUID, form_id: UUID
    ) -> Awaitable[List[ProjectDefinitionNode]]:
        builder = (
            self.get_builder()
            .find_by(
                ProjectNodeFilter(
                    project_id=project_id, display_query_internal_id=form_id
                )
            )
            .finalize()
        )
        results = await self.find_by(builder, order_by=("level", "desc"))
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
                    self._table.c.value,
                    self._table.c.id,
                    self._table.c.path,
                    self._table.c.type_id,
                    self._table.c.type_path,
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
                type_id=record.get("type_id"),
                type_path=split_uuid_path(record.get("type_path")),
                expression=jsonpickle.decode(record.get("value")),
            )
            for record in records
        ]

    async def find_node_on_path_by_type(
        self, project_id: UUID, start_with_path: List[UUID], type_id: UUID
    ) -> Awaitable[List[ProjectNode]]:
        assert len(start_with_path) >= 1, "Cannot start with an path"
        start_with_path_filter = join_uuid_path(start_with_path)
        query = select([self._table]).where(
            and_(
                self._table.c.project_id == project_id,
                self._table.c.type_id == type_id,
                or_(
                    self._table.c.path.like(f"{start_with_path_filter}%"),
                    self._table.c.id == start_with_path[-1],
                ),
            )
        )

        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)
        return results
