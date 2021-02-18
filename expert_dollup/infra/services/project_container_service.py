from sqlalchemy import select, join, and_, desc, or_
from sqlalchemy.sql.expression import func
from typing import List, Optional, Awaitable, Any, Dict
from uuid import UUID
from collections import defaultdict
from expert_dollup.core.domains import (
    ProjectContainer,
    ProjectContainerNode,
    ProjectContainerMeta,
    ProjectDefinitionContainer,
    ProjectContainerTree,
    ProjectContainerFilter,
    FieldNode,
)
from expert_dollup.shared.database_services import BaseCrudTableService
from expert_dollup.infra.path_transform import join_uuid_path, split_uuid_path
from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    project_container_table,
    ProjectContainerDao,
    project_definition_container_table,
    ProjectDefinitionContainerDao,
    project_container_meta_table,
    ProjectContainerMetaDao,
)


class ProjectContainerService(BaseCrudTableService[ProjectContainer]):
    class Meta:
        table = project_container_table
        dao = ProjectContainerDao
        domain = ProjectContainer
        seach_filters = {}
        table_filter_type = ProjectContainerFilter

    async def find_subtree(self, container: ProjectContainer):
        path_filter = join_uuid_path(container.subpath)

        join_definition = self._table.join(
            project_definition_container_table,
            project_definition_container_table.c.id == self._table.c.type_id,
        ).join(
            project_container_meta_table,
            and_(
                project_container_meta_table.c.project_id == container.project_id,
                project_container_meta_table.c.type_id == self._table.c.type_id,
            ),
        )

        query = (
            select(
                [
                    self._table,
                    project_definition_container_table,
                    project_container_meta_table,
                ]
            )
            .select_from(join_definition)
            .where(
                and_(
                    self._table.c.project_id == container.project_id,
                    or_(
                        self._table.c.mixed_paths.op("@>")([path_filter]),
                        self._table.c.id == container.id,
                    ),
                )
            )
            .order_by(desc(func.length(self._table.c.path)))
        )

        records = await self._database.fetch_all(query=query)
        results = self.hydrate_joined_table(
            records,
            [
                (ProjectContainerDao, ProjectContainer, self._table),
                (
                    ProjectDefinitionContainerDao,
                    ProjectDefinitionContainer,
                    project_definition_container_table,
                ),
                (
                    ProjectContainerMetaDao,
                    ProjectContainerMeta,
                    project_container_meta_table,
                ),
            ],
        )

        roots = self._build_tree_from_path(results, join_uuid_path(container.path))
        assert len(roots) == 1, f"Len is {len(roots)}"

        return ProjectContainerTree(roots=roots)

    async def find_children(
        self, project_id: UUID, path: List[UUID]
    ) -> Awaitable[List[ProjectContainer]]:
        path_filter = join_uuid_path(path)
        query = (
            select([self._table])
            .where(
                and_(
                    self._table.c.project_id == project_id,
                    self._table.c.mixed_paths.op("@>")([path_filter]),
                )
            )
            .order_by(desc(func.length(self._table.c.path)))
        )

        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)
        return results

    async def find_children_tree(
        self, project_id: UUID, path: List[UUID], level: Optional[int] = None
    ) -> Awaitable[ProjectContainerTree]:
        path_filter = join_uuid_path(path)
        filter_container = and_(
            project_container_meta_table.c.project_id == project_id,
            project_container_meta_table.c.type_id == self._table.c.type_id,
        )

        if len(path_filter) > 0:
            filter_container = and_(
                filter_container, self._table.c.mixed_paths.op("@>")([path_filter])
            )

        if not level is None:
            filter_container = and_(filter_container, self._table.c.level == level)

        join_definition = self._table.join(
            project_definition_container_table,
            project_definition_container_table.c.id == self._table.c.type_id,
        ).join(
            project_container_meta_table,
            and_(
                project_container_meta_table.c.project_id == project_id,
                project_container_meta_table.c.type_id == self._table.c.type_id,
            ),
        )

        query = (
            select(
                [
                    self._table,
                    project_definition_container_table,
                    project_container_meta_table,
                ]
            )
            .select_from(join_definition)
            .where(and_(self._table.c.project_id == project_id, filter_container))
            .order_by(desc(func.length(self._table.c.path)))
        )

        records = await self._database.fetch_all(query=query)
        results = self.hydrate_joined_table(
            records,
            [
                (ProjectContainerDao, ProjectContainer, self._table),
                (
                    ProjectDefinitionContainerDao,
                    ProjectDefinitionContainer,
                    project_definition_container_table,
                ),
                (
                    ProjectContainerMetaDao,
                    ProjectContainerMeta,
                    project_container_meta_table,
                ),
            ],
        )

        if isinstance(level, int):
            roots = [
                ProjectContainerNode(
                    container=container, definition=definition, meta=meta, children=[]
                )
                for (container, definition, meta), _ in results
            ]
        else:
            roots = self._build_tree_from_path(results, path_filter)

        return ProjectContainerTree(roots=roots)

    async def remove_collection(self, container: ProjectContainer) -> Awaitable:
        path_filter = join_uuid_path(container.subpath)
        query = self._table.delete().where(
            and_(
                or_(
                    self._table.c.mixed_paths.op("@>")([path_filter]),
                    self._table.c.id == container.id,
                ),
                self._table.c.project_id == container.project_id,
            )
        )
        await self._database.execute(query=query)

    def _build_tree_from_path(self, results, path_filter):
        node_map = defaultdict(list)
        tree_depth = None

        for ((container, definition, meta), (container_dao, _, __)) in results:
            node = ProjectContainerNode(
                container=container, definition=definition, meta=meta, children=[]
            )

            node_map[container_dao.path].append(node)

            if tree_depth is None:
                tree_depth = len(node.container.path)

            if len(node.container.path) < tree_depth:
                children_path = join_uuid_path(
                    [*node.container.path, node.container.id]
                )

                assert children_path in node_map
                node.children = sorted(
                    node_map[children_path], key=lambda child: child.container.type_id
                )

        if len(node_map) == 0:
            roots = []
        else:
            assert path_filter in node_map, "The tree must have a root"
            roots = node_map[path_filter]

        return roots

    async def get_all_fields(self, project_id: UUID) -> Awaitable[List[FieldNode]]:
        join_definition = self._table.join(
            project_definition_container_table,
            project_definition_container_table.c.id == self._table.c.type_id,
        )

        query = (
            select(
                [
                    project_definition_container_table.c.name,
                    project_definition_container_table.c.id,
                    project_definition_container_table.c.path,
                    self._table.c.value,
                ]
            )
            .select_from(join_definition)
            .where(
                and_(
                    self._table.c.project_id == project_id,
                    self._table.c.value.op("->")("value") != None,
                )
            )
        )

        records = await self._database.fetch_all(query=query)

        return [
            FieldNode(
                id=record.get("id"),
                name=record.get("name"),
                path=split_uuid_path(record.get("path")),
                expression=record.get("value")["value"],
            )
            for record in records
        ]
