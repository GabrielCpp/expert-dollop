from typing import Awaitable
from uuid import UUID
from predykt.core.exceptions import RessourceNotFound
from predykt.core.domains import Project
from predykt.infra.services import ProjectService


class ProjectUseCase:
    def __init__(
        self,
        service: ProjectService
    ):
        self.service = service

    async def add(self, domain: Project) -> Awaitable:
        await self.service.insert(domain)

    async def remove_by_id(self, id: UUID) -> Awaitable:
        await self.service.delete_by_id(id)

    async def update(self, domain: Project) -> Awaitable:
        await self.service.update(domain)

    async def find_by_id(self, id: UUID) -> Awaitable[Project]:
        result = await self.service.find_by_id(id)

        if result is None:
            raise RessourceNotFound()

        return result
