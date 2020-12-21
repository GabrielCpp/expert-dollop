from uuid import UUID, uuid4
from typing import Awaitable
from predykt.core.exceptions import RessourceNotFound
from predykt.core.domains import ProjectDefinition, Ressource
from predykt.infra.services import ProjectDefinitionService, RessourceService, ProjectDefinitionPluginService
from predykt.infra.providers import WordProvider


class ProjectDefinitonUseCase:
    def __init__(
        self,
        service: ProjectDefinitionService,
        ressource_service: RessourceService,
        word_provider: WordProvider,
        project_definition_plugin_service: ProjectDefinitionPluginService,
    ):
        self.service = service
        self.ressource_service = ressource_service
        self.word_provider = word_provider
        self.project_definition_plugin_service = project_definition_plugin_service

    async def add(self, domain: ProjectDefinition) -> Awaitable:
        suffix_name = self.word_provider.pick_join(3)
        name = 'project_definition_' + suffix_name + domain.id.hex()
        ressource = Ressource(
            id=domain.id,
            name=name,
            owner_id=uuid4()
        )

        await self._ensure_plugin_config_valid(domain)
        await self.ressource_service.insert(ressource)
        await self.service.insert(domain)

    async def remove_by_id(self, id: UUID) -> Awaitable:
        await self.service.delete_by_id(id)
        await self.ressource_service.delete_by_id(id)

    async def update(self, domain: ProjectDefinition) -> Awaitable:
        await self._ensure_plugin_config_valid(domain)
        await self.service.update(domain)

    async def find_by_id(self, id: UUID) -> Awaitable[ProjectDefinition]:
        result = await self.service.find_by_id(id)

        if result is None:
            raise RessourceNotFound()

        return result

    async def _ensure_plugin_config_valid(self, domain: ProjectDefinition) -> None:
        if not await self.project_definition_plugin_service.has_every_id(domain.plugins):
            raise RessourceNotFound("One or more plugin not found")
