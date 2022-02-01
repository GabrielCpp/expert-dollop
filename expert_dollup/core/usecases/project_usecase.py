from typing import Awaitable
from uuid import UUID
from expert_dollup.core.domains import (
    Project,
    ProjectDetails,
    ProjectNodeFilter,
)
from expert_dollup.core.builders import ProjectBuilder
from expert_dollup.infra.services import (
    ProjectService,
    RessourceService,
    ProjectNodeService,
    ProjectNodeMetaService,
)

from expert_dollup.shared.starlette_injection import LoggerFactory


class ProjectUseCase:
    def __init__(
        self,
        project_service: ProjectService,
        project_node_service: ProjectNodeService,
        project_node_meta_service: ProjectNodeMetaService,
        ressource_service: RessourceService,
        project_builder: ProjectBuilder,
        logger: LoggerFactory,
    ):
        self.project_service = project_service
        self.project_node_service = project_node_service
        self.project_node_meta_service = project_node_meta_service
        self.ressource_service = ressource_service
        self.project_builder = project_builder
        self.logger = logger.create(__name__)

    async def add(self, project_details: ProjectDetails) -> Awaitable[ProjectDetails]:
        project = await self.project_builder.build_new(project_details)
        await self._insert_new_project(project)

        return project.details

    async def clone(self, project_id: UUID) -> Awaitable[ProjectDetails]:
        project_details = await self.project_service.find_by_id(project_id)
        cloned_project = await self.project_builder.clone(project_details)
        await self._insert_new_project(cloned_project)

        return cloned_project.details

    async def delete_by_id(self, project_id: UUID) -> Awaitable:
        await self.project_node_service.delete_by(
            ProjectNodeFilter(project_id=project_id)
        )
        await self.project_node_meta_service.delete_by(
            ProjectNodeFilter(project_id=project_id)
        )
        await self.project_service.delete_by_id(project_id)
        await self.ressource_service.delete_by_id(project_id)

    async def find_by_id(self, id: UUID) -> Awaitable[ProjectDetails]:
        result = await self.project_service.find_by_id(id)
        return result

    async def _insert_new_project(self, project: Project):
        await self.ressource_service.insert(project.ressource)
        await self.project_service.insert(project.details)
        await self.project_node_meta_service.insert_many(project.metas)
        await self.project_node_service.insert_many(project.nodes)
