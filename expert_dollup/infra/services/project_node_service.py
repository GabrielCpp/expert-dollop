from typing import List, Optional, Awaitable
from uuid import UUID
from expert_dollup.core.domains import (
    ProjectNode,
    ProjectDefinitionNode,
    ProjectNodeFilter,
)
from expert_dollup.shared.database_services import CollectionServiceProxy
from expert_dollup.infra.expert_dollup_db import ProjectNodeDao, FIELD_LEVEL


class ProjectNodeService(CollectionServiceProxy[ProjectNode]):
    class Meta:
        dao = ProjectNodeDao
        domain = ProjectNode

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

    async def get_all_fields(self, project_id: UUID) -> List[ProjectNode]:
        builder = (
            self.get_builder()
            .find_by(ProjectNodeFilter(project_id=project_id, level=FIELD_LEVEL))
            .finalize()
        )

        nodes = await self.find_by(builder)

        return nodes

    async def find_node_on_path_by_type(
        self, project_id: UUID, start_with_path: List[UUID], type_id: UUID
    ) -> Awaitable[List[ProjectNode]]:
        assert len(start_with_path) >= 1, "Cannot start with an path"
        builder = (
            self.get_builder()
            .find_by(ProjectNodeFilter(project_id=project_id, type_id=type_id))
            .save("find_node_of_type_in_project")
            .find_by(ProjectNodeFilter(id=start_with_path[-1]))
            .startwiths(ProjectNodeFilter(path=start_with_path))
            .any_of()
            .save("find_instances_by_path")
            .all_of("find_node_of_type_in_project", "find_instances_by_path")
            .finalize()
        )

        results = await self.find_by(builder)
        return results
