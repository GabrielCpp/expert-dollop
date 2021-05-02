import structlog
from typing import Awaitable
from uuid import UUID
from expert_dollup.core.domains import (
    Project,
    ProjectDetails,
    ProjectContainer,
    ProjectContainerMeta,
    ProjectContainerFilter,
)
from expert_dollup.core.builders import ProjectBuilder
from expert_dollup.infra.services import (
    ProjectService,
    RessourceService,
    ProjectContainerService,
    ProjectContainerMetaService,
)

logger = structlog.get_logger(__name__)


class ProjectUseCase:
    def __init__(
        self,
        project_service: ProjectService,
        project_container_service: ProjectContainerService,
        project_container_meta_service: ProjectContainerMetaService,
        ressource_service: RessourceService,
        project_builder: ProjectBuilder,
    ):
        self.project_service = project_service
        self.project_container_service = project_container_service
        self.project_container_meta_service = project_container_meta_service
        self.ressource_service = ressource_service
        self.project_builder = project_builder

    async def add(self, project_details: ProjectDetails) -> Awaitable[ProjectDetails]:
        project = await self.project_builder.build_new(project_details)
        await self._insert_new_project(project)

        return project.details

    async def clone(self, project_id: UUID) -> Awaitable[ProjectDetails]:
        project_details = await self.project_service.find_by_id(project_id)
        cloned_project = await self.project_builder.clone(project_details)
        await self._insert_new_project(cloned_project)

        return cloned_project.details

    async def remove_by_id(self, project_id: UUID) -> Awaitable:
        await self.project_container_service.remove_by(
            ProjectContainerFilter(project_id=project_id)
        )
        await self.project_container_meta_service.remove_by(
            ProjectContainerFilter(project_id=project_id)
        )
        await self.project_service.delete_by_id(project_id)
        await self.ressource_service.delete_by_id(project_id)

    async def find_by_id(self, id: UUID) -> Awaitable[ProjectDetails]:
        result = await self.project_service.find_by_id(id)
        return result

    async def _insert_new_project(self, project: Project):
        await self.ressource_service.insert(project.ressource)
        await self.project_service.insert(project.details)
        await self.project_container_meta_service.insert_many(project.metas)
        await self.project_container_service.insert_many(project.nodes)
