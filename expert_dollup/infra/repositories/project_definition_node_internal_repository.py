from typing import List, Dict, Optional
from uuid import UUID
from expert_dollup.shared.database_services import (
    RepositoryProxy,
    InternalRepository,
)
from expert_dollup.core.domains import (
    ProjectDefinitionNode,
    ProjectDefinitionNodeFilter,
)
from expert_dollup.infra.expert_dollup_db import ProjectDefinitionNodeDao
from expert_dollup.core.utils.path_transform import join_uuid_path


class ProjectDefinitionNodeInternalRepository(RepositoryProxy[ProjectDefinitionNode]):
    def __init__(self, repository: InternalRepository[ProjectDefinitionNode]):
        RepositoryProxy.__init__(self, repository)
        self._repository = repository

    async def get_fields_id_by_name(
        self, project_definition_id: UUID, names: Optional[List[str]] = None
    ) -> Dict[str, UUID]:

        query = (
            self._repository.get_builder()
            .select("id", "name")
            .where("project_definition_id", "==", project_definition_id)
        )

        if not names is None:
            if len(names) == 0:
                return {}

            query = query.where("name", "in", names)

        records = await self._repository.fetch_all_records(query)

        return {record.get("name"): UUID(str(record.get("id"))) for record in records}

    async def has_path(self, path: List[UUID]) -> bool:
        if len(path) == 0:
            return True

        parent_id = path[-1]
        parent_path = path[0:-1]
        count = await self.exists(
            ProjectDefinitionNodeFilter(path=parent_path, id=parent_id)
        )

        return count > 0

    async def delete_child_of(self, id: UUID):
        value = await self.find_by_id(id)
        query = (
            self._repository.get_builder()
            .where("project_definition_id", "==", value.project_definition_id)
            .where("path", "startwiths", join_uuid_path(value.subpath))
        )

        await self.delete_by(query)

    async def find_children(
        self, project_definition_id: UUID, path: List[UUID]
    ) -> List[ProjectDefinitionNode]:
        query = self._repository.get_builder().where(
            "project_definition_id", "==", project_definition_id
        )

        if len(path) > 0:
            query.where("path", "startwiths", join_uuid_path(path))

        results = await self.find_by(query)

        return sorted(results, key=lambda x: len(x.path))

    async def find_root_sections(
        self, project_definition_id: UUID
    ) -> List[ProjectDefinitionNode]:
        query = (
            self._repository.get_builder()
            .where("project_definition_id", "==", project_definition_id)
            .where("display_query_internal_id", "==", project_definition_id)
            .orderby(("level", "desc"))
        )

        results = await self.find_by(query)

        return results

    async def find_root_section_nodes(
        self, project_definition_id: UUID, root_section_id: UUID
    ) -> List[ProjectDefinitionNode]:
        query = (
            self._repository.get_builder()
            .where("project_definition_id", "==", project_definition_id)
            .where("display_query_internal_id", "==", root_section_id)
            .orderby(("level", "desc"))
        )

        results = await self.find_by(query)

        return results

    async def find_form_content(
        self, project_definition_id: UUID, form_id: UUID
    ) -> List[ProjectDefinitionNode]:
        query = (
            self._repository.get_builder()
            .where("project_definition_id", "==", project_definition_id)
            .where("display_query_internal_id", "==", form_id)
            .orderby(("level", "desc"))
        )

        results = await self.find_by(query)

        return results
