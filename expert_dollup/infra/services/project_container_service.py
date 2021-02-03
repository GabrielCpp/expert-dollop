from sqlalchemy import select, join, and_, desc
from typing import List
from uuid import UUID
from collections import defaultdict
from expert_dollup.core.domains import (
    ProjectContainer,
    ProjectContainerNode,
    ProjectContainerMeta,
    ProjectDefinitionContainer,
    ProjectContainerTree,
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
        table_filter_type = None

    async def find_container_tree_by_path(self, project_id: UUID, path: List[UUID]):
        path_filter = join_uuid_path(path)
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
            .where(self._table.c.project_id == project_id)
            .order_by(desc(self._table.c.path))
        )

        # self._table.c.path == path_filter,
        records = await self._database.fetch_all(query=query)

        def slice_record(record, delta, columns):
            mapped = {}

            for index, column in enumerate(columns):
                mapped[column.name] = record[delta + index]

            return mapped

        def hydrate_joined_table(mapper, records, dao_table_pairs):
            for record in records:
                offset = 0
                domains = []
                daos = []

                for (dao_type, domain_type, table) in dao_table_pairs:
                    dao = dao_type(**slice_record(record, offset, table.c))
                    daos.append(dao)

                    domain = mapper.map(dao, domain_type, dao_type)
                    domains.append(domain)

                    offset += len(table.c)

                yield domains, daos

        results = hydrate_joined_table(
            self._mapper,
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

        node_map = defaultdict(list)
        tree_depth = None

        for ((container, definition, meta), (container_dao, _, __)) in results:
            node = ProjectContainerNode(
                container=container, definition=definition, meta=meta, children=[]
            )

            node_map[container_dao.path].append(node)

            if tree_depth is None:
                tree_depth = len(node.container.path)

            if tree_depth < len(node.container.path):
                children_path = join_uuid_path(
                    [*node.container.path, node.container.id]
                )
                assert children_path in node_map

                node.children = node_map[children_path]

        assert "" in node_map
        roots = node_map[""]

        return ProjectContainerTree(roots=roots)
