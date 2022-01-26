from uuid import UUID, uuid4
from typing import Awaitable
from expert_dollup.core.exceptions import RessourceNotFound
from expert_dollup.core.domains import ProjectDefinition, Ressource
from expert_dollup.infra.services import (
    ProjectDefinitionService,
    RessourceService,
)
from expert_dollup.infra.providers import WordProvider


class ProjectDefinitonUseCase:
    def __init__(
        self,
        service: ProjectDefinitionService,
        ressource_service: RessourceService,
        word_provider: WordProvider,
    ):
        self.service = service
        self.ressource_service = ressource_service
        self.word_provider = word_provider

    async def add(self, domain: ProjectDefinition) -> Awaitable:
        ressource = Ressource(id=domain.id, kind="project_definition", owner_id=uuid4())
        await self.ressource_service.insert(ressource)
        await self.service.insert(domain)
        return domain

    async def delete_by_id(self, id: UUID) -> Awaitable:
        await self.service.delete_by_id(id)
        await self.ressource_service.delete_by_id(id)

    async def update(self, domain: ProjectDefinition) -> Awaitable:
        await self.service.update(domain)
        return await self.find_by_id(domain.id)

    async def find_by_id(self, id: UUID) -> Awaitable[ProjectDefinition]:
        result = await self.service.find_by_id(id)

        if result is None:
            raise RessourceNotFound()

        return result
