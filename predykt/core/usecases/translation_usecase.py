
from typing import Awaitable
from predykt.core.exceptions import RessourceNotFound, ValidationError
from predykt.core.domains import Translation, TranslationId, Ressource, TranslationRessourceLocaleQuery
from predykt.infra.services import TranslationService, RessourceService


class TranslationUseCase:
    def __init__(
        self,
        service: TranslationService,
        ressource_service: RessourceService
    ):
        self.service = service
        self.ressource_service = ressource_service

    async def add(self, domain: Translation) -> Awaitable:
        if not await self.ressource_service.has(domain.ressource_id):
            raise ValidationError.for_field(
                "ressource_id", "Missing an attached ressource")

        await self.service.insert(domain)

    async def remove_by_id(self, id: TranslationId) -> Awaitable:
        await self.service.delete_by_id(id)

    async def update(self, domain: Translation) -> Awaitable:
        if not await self.ressource_service.has(domain.ressource_id):
            raise ValidationError.for_field(
                "ressource_id", "Missing an attached ressource")

        await self.service.update(domain)

    async def find_by_id(self, id: TranslationId) -> Awaitable[Translation]:
        result = await self.service.find_by_id(id)

        if result is None:
            raise RessourceNotFound()

        return result

    async def find_by_ressource_locale(self, query: TranslationRessourceLocaleQuery):
        return await self.service.find_by(query)
