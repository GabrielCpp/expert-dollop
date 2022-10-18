from uuid import UUID
from expert_dollup.shared.starlette_injection import Clock
from expert_dollup.shared.database_services import DatabaseContext
from expert_dollup.core.exceptions import RessourceNotFound
from expert_dollup.core.domains import *
from expert_dollup.infra.providers import WordProvider
from expert_dollup.core.utils.ressource_permissions import authorization_factory


class ProjectDefinitonUseCase:
    def __init__(
        self,
        db_context: DatabaseContext,
        word_provider: WordProvider,
        clock: Clock,
    ):
        self.db_context = db_context
        self.word_provider = word_provider
        self.clock = clock

    async def add(self, domain: ProjectDefinition, user: User) -> ProjectDefinition:
        ressource = authorization_factory.allow_access_to(domain, user)
        await self.db_context.insert(Ressource, ressource)
        await self.db_context.insert(ProjectDefinition, domain)
        return domain

    async def delete_by_id(self, id: UUID) -> None:
        definition = await self.db_context.find_by_id(ProjectDefinition, id)
        await self.db_context.delete_by_id(ProjectDefinition, id)
        await self.db_context.delete_by(Ressource, RessourceFilter(id=id))

    async def update(self, domain: ProjectDefinition) -> ProjectDefinition:
        await self.db_context.upserts(ProjectDefinition, [domain])
        return domain

    async def find_by_id(self, id: UUID) -> ProjectDefinition:
        return await self.db_context.find_by_id(ProjectDefinition, id)
