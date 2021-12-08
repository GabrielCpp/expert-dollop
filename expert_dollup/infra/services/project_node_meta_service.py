from typing import Awaitable, List
from uuid import UUID
from expert_dollup.infra.expert_dollup_db import ProjectNodeMetaDao
from expert_dollup.core.domains import ProjectNodeMeta, ProjectNodeMetaFilter
from expert_dollup.shared.database_services import CollectionServiceProxy


class ProjectNodeMetaService(CollectionServiceProxy[ProjectNodeMeta]):
    class Meta:
        dao = ProjectNodeMetaDao
        domain = ProjectNodeMeta
        table_filter_type = ProjectNodeMetaFilter

    async def find_root_sections(
        self, project_id: UUID
    ) -> Awaitable[List[ProjectNodeMeta]]:
        results = await self.find_by(
            ProjectNodeMetaFilter(
                project_id=project_id, display_query_internal_id=project_id
            ),
        )

        return sorted(results, key=lambda x: len(x.definition.path))

    async def find_root_section_nodes(
        self, project_id: UUID, root_section_def_id: UUID
    ) -> Awaitable[List[ProjectNodeMeta]]:
        results = await self.find_by(
            ProjectNodeMetaFilter(
                project_id=project_id, display_query_internal_id=root_section_def_id
            ),
        )
        return sorted(results, key=lambda x: len(x.definition.path))

    async def find_form_content(
        self, project_id: UUID, form_def_id: UUID
    ) -> Awaitable[List[ProjectNodeMeta]]:
        results = await self.find_by(
            ProjectNodeMetaFilter(
                project_id=project_id, display_query_internal_id=form_def_id
            ),
        )
        return sorted(results, key=lambda x: len(x.definition.path))
