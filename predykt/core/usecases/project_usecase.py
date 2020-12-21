from typing import Awaitable
from uuid import UUID
from predykt.core.exceptions import RessourceNotFound
from predykt.core.domains import Project
from predykt.infra.services import ProjectService, RessourceService
from predykt.infra.providers import WordProvider


class ProjectUseCase:
    def __init__(
        self,
        service: ProjectService,
        ressource_service: RessourceService,
        word_provider: WordProvider
    ):
        self.service = service
        self.ressource_service = ressource_service
        self.word_provider = word_provider

    async def add(self, domain: Project) -> Awaitable:
        suffix_name = self.word_provider.pick_join(3)
        name = 'project_definition_' + suffix_name + domain.id.hex()
        ressource = Ressource(
            id=domain.id,
            name=name,
            owner_id=uuid4()
        )

        await self.ressource_service.insert(ressource)
        await self.service.insert(domain)

    async def remove_by_id(self, id: UUID) -> Awaitable:
        await self.service.delete_by_id(id)
        await self.ressource_service.delete_by_id(id)

    async def update(self, domain: Project) -> Awaitable:
        await self.service.update(domain)

    async def find_by_id(self, id: UUID) -> Awaitable[Project]:
        result = await self.service.find_by_id(id)

        if result is None:
            raise RessourceNotFound()

        return result
