from typing import List, Dict
from uuid import UUID
from expert_dollup.shared.database_services import (
    CollectionServiceProxy,
    IdStampedDateCursorEncoder,
)
from expert_dollup.core.domains import (
    ProjectDefinitionNode,
    ProjectDefinitionNodeFilter,
    ProjectDefinitionNodePluckFilter,
)
from expert_dollup.infra.expert_dollup_db import ProjectDefinitionNodeDao


class ProjectDefinitionNodeService(CollectionServiceProxy[ProjectDefinitionNode]):
    class Meta:
        dao = ProjectDefinitionNodeDao
        domain = ProjectDefinitionNode
        table_filter_type = ProjectDefinitionNodeFilter
        paginator = IdStampedDateCursorEncoder.for_fields("name", str, str, "")

    async def get_fields_by_name(
        self, project_def_id: UUID, names: List[str]
    ) -> Dict[str, UUID]:
        if len(names) == 0:
            return {}

        query = (
            self.get_builder()
            .select_fields("id", "name")
            .find_by(ProjectDefinitionNodeFilter(project_def_id=project_def_id))
            .pluck(ProjectDefinitionNodePluckFilter(names=names))
            .finalize()
        )
        records = await self.fetch_all_records(query)

        return {record.get("name"): record.get("id") for record in records}

    async def has_path(self, path: List[UUID]) -> bool:
        if len(path) == 0:
            return True

        parent_id = path[-1]
        parent_path = path[0:-1]
        count = await self.count(
            ProjectDefinitionNodeFilter(path=parent_path, id=parent_id)
        )

        return count > 0

    async def delete_child_of(self, id: UUID):
        value = await self.find_by_id(id)
        query = (
            self.get_builder()
            .find_by(ProjectDefinitionNodeFilter(project_def_id=value.project_def_id))
            .startwiths(ProjectDefinitionNodeFilter(path=value.subpath))
            .finalize()
        )

        await self.delete_by(query)

    async def find_children(
        self, project_def_id: UUID, path: List[UUID]
    ) -> List[ProjectDefinitionNode]:
        query = (
            self.get_builder()
            .find_by(ProjectDefinitionNodeFilter(project_def_id=project_def_id))
            .startwiths(ProjectDefinitionNodeFilter(path=path))
            .finalize()
        )

        results = await self.find_by(query, order_by=("level", "desc"))

        return results

    async def find_root_sections(
        self, project_def_id: UUID
    ) -> List[ProjectDefinitionNode]:
        query = (
            self.get_builder()
            .find_by(
                ProjectDefinitionNodeFilter(
                    project_def_id=project_def_id,
                    display_query_internal_id=project_def_id,
                )
            )
            .finalize()
        )

        results = await self.find_by(query, order_by=("level", "desc"))

        return results

    async def find_root_section_nodes(
        self, project_def_id: UUID, root_section_id: UUID
    ) -> List[ProjectDefinitionNode]:
        query = (
            self.get_builder()
            .find_by(
                ProjectDefinitionNodeFilter(
                    project_def_id=project_def_id,
                    display_query_internal_id=root_section_id,
                )
            )
            .finalize()
        )

        results = await self.find_by(query, order_by=("level", "desc"))

        return results

    async def find_form_content(
        self, project_def_id: UUID, form_id: UUID
    ) -> List[ProjectDefinitionNode]:
        query = (
            self.get_builder()
            .find_by(
                ProjectDefinitionNodeFilter(
                    project_def_id=project_def_id,
                    display_query_internal_id=form_id,
                )
            )
            .finalize()
        )

        results = await self.find_by(query, order_by=("level", "desc"))

        return results
