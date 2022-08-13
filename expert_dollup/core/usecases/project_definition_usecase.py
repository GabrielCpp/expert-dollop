from uuid import UUID
from expert_dollup.shared.database_services import CollectionService
from expert_dollup.core.exceptions import RessourceNotFound
from expert_dollup.core.domains import *
from expert_dollup.infra.providers import WordProvider
from expert_dollup.core.utils.ressource_permissions import make_ressource


class ProjectDefinitonUseCase:
    def __init__(
        self,
        service: CollectionService[ProjectDefinition],
        ressource_service: CollectionService[Ressource],
        word_provider: WordProvider,
    ):
        self.service = service
        self.ressource_service = ressource_service
        self.word_provider = word_provider

    async def add(self, domain: ProjectDefinition, user: User) -> ProjectDefinition:
        ressource = make_ressource(ProjectDefinition, domain, user)
        await self.ressource_service.insert(ressource)
        await self.service.insert(domain)
        return domain

    async def delete_by_id(self, id: UUID) -> None:
        await self.service.delete_by_id(id)
        await self.ressource_service.delete_by((RessourceFilter(id=id)))

    async def update(self, domain: ProjectDefinition) -> ProjectDefinition:
        await self.service.update(
            ProjectDefinitionFilter(
                name=domain.name,
                default_datasheet_id=domain.default_datasheet_id,
                properties=domain.properties,
            ),
            ProjectDefinitionFilter(id=domain.id),
        )
        return domain

    async def find_by_id(self, id: UUID) -> ProjectDefinition:
        result = await self.service.find_by_id(id)

        if result is None:
            raise RessourceNotFound()

        return result
