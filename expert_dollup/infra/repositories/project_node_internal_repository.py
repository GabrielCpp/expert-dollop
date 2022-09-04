from typing import List, Optional
from uuid import UUID
from expert_dollup.core.domains import (
    ProjectNode,
    ProjectDefinitionNode,
    ProjectNodeFilter,
)
from expert_dollup.shared.database_services import (
    RepositoryProxy,
    InternalRepository,
    PluckQuery,
)
from expert_dollup.infra.expert_dollup_db import ProjectNodeDao, FIELD_LEVEL
from expert_dollup.core.utils.path_transform import join_uuid_path


class ProjectNodeInternalRepository(
    RepositoryProxy[ProjectNode], PluckQuery[ProjectNode]
):
    def __init__(self, repository: InternalRepository[ProjectNode]):
        RepositoryProxy.__init__(self, repository)
        PluckQuery.__init__(self, repository)
        self._repository = repository

    async def find_children(
        self, project_id: UUID, path: List[UUID], level: Optional[int] = None
    ) -> List[ProjectNode]:
        builder = self._repository.get_builder().where("project_id", "==", project_id)

        if not level is None:
            builder.where("level", "==", level)

        if len(path) > 0:
            builder.where("path", "startwiths", join_uuid_path(path))

        results = await self.find_by(builder)

        return sorted(results, key=lambda x: len(x.path))

    async def remove_collection(self, container: ProjectNode) -> None:
        builder = (
            self._repository.get_builder()
            .where("project_id", "==", container.project_id)
            .where("path", "startwiths", join_uuid_path(container.subpath))
        )

        await self.delete_by(builder)

    async def find_root_sections(self, project_id: UUID) -> List[ProjectNode]:
        builder = (
            self._repository.get_builder()
            .where("project_id", "==", project_id)
            .where("display_query_internal_id", "==", project_id)
            .orderby(("level", "desc"))
        )
        results = await self.find_by(builder)
        return results

    async def find_root_section_nodes(
        self, project_id: UUID, root_section_id: UUID
    ) -> List[ProjectNode]:
        builder = (
            self._repository.get_builder()
            .where("project_id", "==", project_id)
            .where("display_query_internal_id", "==", root_section_id)
            .orderby(("level", "desc"))
        )
        results = await self.find_by(builder)
        return results

    async def find_form_content(
        self, project_id: UUID, form_id: UUID
    ) -> List[ProjectNode]:
        builder = (
            self._repository.get_builder()
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
    ) -> List[ProjectNode]:
        assert len(start_with_path) >= 1, "Cannot start with an path"

        by_id_query = (
            self._repository.get_builder()
            .where("project_id", "==", project_id)
            .where("type_id", "==", type_id)
            .where("id", "==", start_with_path[-1])
        )

        by_path_query = (
            self._repository.get_builder()
            .where("project_id", "==", project_id)
            .where("type_id", "==", type_id)
            .where("path", "startwiths", join_uuid_path(start_with_path))
        )

        results = await self.find_by(by_id_query)
        other_results = await self.find_by(by_path_query)
        results.extend(other_results)

        return results
