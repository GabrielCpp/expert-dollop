from typing import List, Optional, Awaitable
from uuid import UUID
from expert_dollup.core.domains import (
    ProjectNode,
    ProjectDefinitionNode,
    ProjectNodeFilter,
)
from expert_dollup.shared.database_services import CollectionServiceProxy
from expert_dollup.infra.expert_dollup_db import ProjectNodeDao, FIELD_LEVEL
from expert_dollup.core.utils.path_transform import join_uuid_path


class ProjectNodeService(CollectionServiceProxy[ProjectNode]):
    class Meta:
        dao = ProjectNodeDao
        domain = ProjectNode

    async def find_children(
        self, project_id: UUID, path: List[UUID], level: Optional[int] = None
    ) -> Awaitable[ProjectNode]:
        builder = (
            self.get_builder()
            .where("project_id", "==", project_id)
            .where("path", "startwiths", join_uuid_path(path))
            .orderby(("level", "desc"))
        )

        if not level is None:
            builder.where("level", "==", level)

        results = await self.find_by(builder)

        return results

    async def remove_collection(self, container: ProjectNode) -> Awaitable:
        builder = (
            self.get_builder()
            .where("project_id", "==", container.project_id)
            .where("path", "startwiths", join_uuid_path(container.subpath))
        )

        await self.delete_by(builder)

    async def find_root_sections(
        self, project_id: UUID
    ) -> Awaitable[List[ProjectDefinitionNode]]:
        builder = (
            self.get_builder()
            .where("project_id", "==", project_id)
            .where("display_query_internal_id", "==", project_id)
            .orderby(("level", "desc"))
        )
        results = await self.find_by(builder)
        return results

    async def find_root_section_nodes(
        self, project_id: UUID, root_section_id: UUID
    ) -> Awaitable[List[ProjectDefinitionNode]]:
        builder = (
            self.get_builder()
            .where("project_id", "==", project_id)
            .where("display_query_internal_id", "==", root_section_id)
            .orderby(("level", "desc"))
        )
        results = await self.find_by(builder)
        return results

    async def find_form_content(
        self, project_id: UUID, form_id: UUID
    ) -> Awaitable[List[ProjectDefinitionNode]]:
        builder = (
            self.get_builder()
            .where("project_id", "==", project_id)
            .where("display_query_internal_id", "==", form_id)
            .orderby(("level", "desc"))
        )
        results = await self.find_by(builder)
        return results

    async def get_all_fields(self, project_id: UUID) -> List[ProjectNode]:
        nodes = await self.find_by(
            ProjectNodeFilter(project_id=project_id, level=FIELD_LEVEL)
        )

        return nodes

    async def find_node_on_path_by_type(
        self, project_id: UUID, start_with_path: List[UUID], type_id: UUID
    ) -> Awaitable[List[ProjectNode]]:
        assert len(start_with_path) >= 1, "Cannot start with an path"

        by_id_query = (
            self.get_builder()
            .where("project_id", "==", project_id)
            .where("type_id", "==", type_id)
            .where("id", "==", start_with_path[-1])
        )

        by_path_query = (
            self.get_builder()
            .where("project_id", "==", project_id)
            .where("type_id", "==", type_id)
            .where("path", "startwiths", join_uuid_path(start_with_path))
        )

        results = await self.find_by(by_id_query)
        other_results = await self.find_by(by_path_query)
        results.extend(other_results)

        return results
