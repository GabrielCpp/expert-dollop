from typing import List
from uuid import UUID
from expert_dollup.infra.expert_dollup_db import (
    ProjectNodeMetaDao,
    ProjectDefinitionNodeDao,
)
from expert_dollup.core.domains import (
    ProjectNodeMeta,
    ProjectNodeMetaFilter,
    ProjectDefinitionNode,
)
from expert_dollup.shared.database_services import (
    CollectionServiceProxy,
    CollectionMapper,
)


class ProjectNodeMetaService(CollectionServiceProxy[ProjectNodeMeta]):
    class Meta:
        dao = ProjectNodeMetaDao
        domain = ProjectNodeMeta

    async def find_project_defs(self, project_id: UUID) -> List[ProjectDefinitionNode]:
        builder = (
            self.get_builder()
            .select("definition")
            .where("project_id", "==", project_id)
        )

        records = await self.fetch_all_records(
            builder,
            {
                "definition": lambda mapper: CollectionMapper(
                    mapper,
                    ProjectDefinitionNode,
                    ProjectDefinitionNodeDao,
                    getattr(ProjectDefinitionNodeDao.Meta, "version", None),
                    getattr(ProjectDefinitionNodeDao.Meta, "version_mappers", {}),
                ).map_to_domain
            },
        )

        return [record.get("definition") for record in records]

    async def find_root_sections(self, project_id: UUID) -> List[ProjectNodeMeta]:
        results = await self.find_by(
            ProjectNodeMetaFilter(
                project_id=project_id, display_query_internal_id=project_id
            ),
        )

        return sorted(results, key=lambda x: len(x.definition.path))

    async def find_root_section_nodes(
        self, project_id: UUID, root_section_def_id: UUID
    ) -> List[ProjectNodeMeta]:
        results = await self.find_by(
            ProjectNodeMetaFilter(
                project_id=project_id, display_query_internal_id=root_section_def_id
            ),
        )
        return sorted(results, key=lambda x: len(x.definition.path))

    async def find_form_content(
        self, project_id: UUID, form_def_id: UUID
    ) -> List[ProjectNodeMeta]:
        results = await self.find_by(
            ProjectNodeMetaFilter(
                project_id=project_id, display_query_internal_id=form_def_id
            ),
        )
        return sorted(results, key=lambda x: len(x.definition.path))
