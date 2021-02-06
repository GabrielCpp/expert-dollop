from sqlalchemy import select, join, and_, desc
from sqlalchemy.sql.expression import func
from typing import List, Optional
from uuid import UUID
from collections import defaultdict
from expert_dollup.core.domains import (
    ProjectContainer,
    ProjectContainerNode,
    ProjectContainerMeta,
    ProjectDefinitionContainer,
    ProjectContainerTree,
    ProjectContainerFilter,
)
from expert_dollup.shared.database_services import BaseCrudTableService
from expert_dollup.infra.path_transform import join_uuid_path
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

    async def find_container_tree_by_path(
        self, project_id: UUID, path: List[UUID], level: Optional[int] = None
    ):
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
        ).join(project_container_meta_table, filter_container)

        query = (
            select(
                [
                    self._table,
                    project_definition_container_table,
                    project_container_meta_table,
                ]
            )
            .select_from(join_definition)
            .where(self._table.c.project_id == project_id)
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
                node.children = node_map[children_path]

        if len(node_map) == 0:
            roots = []
        else:
            assert path_filter in node_map, "The tree must have a root"
            roots = node_map[path_filter]

        return roots
