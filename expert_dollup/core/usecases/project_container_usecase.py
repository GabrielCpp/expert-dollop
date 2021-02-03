from typing import Awaitable, List
from uuid import UUID
from expert_dollup.core.domains import ProjectContainer, ProjectContainerTree
from expert_dollup.infra.services import ProjectContainerService
from expert_dollup.shared.database_services import Page


class ProjectContainerUseCase:
    def __init__(self, project_container_service: ProjectContainerService):
        self.project_container_service = project_container_service

    async def find_by_id(self, id: UUID) -> Awaitable[ProjectContainer]:
        container = await self.project_container_service.find_by_id(id)
        return container

    async def find_by_path(
        self, project_id: UUID, path: List[UUID]
    ) -> Awaitable[ProjectContainerTree]:
        return await self.project_container_service.find_container_tree_by_path(
            project_id, path
        )

    async def remove(self, id: UUID) -> Awaitable:
        await self.project_container_service.remove(id)

    async def clone_collection(self, container_id: UUID):
        pass

    async def add_collection(self, project_id: UUID, container_type_id: UUID):
        pass
