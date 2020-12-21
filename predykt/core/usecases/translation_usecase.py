
from typing import Awaitable
from uuid import UUID
from predykt.core.exceptions import RessourceNotFound
from predykt.core.domains import Translation, Ressource
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
        await self.service.insert(domain)

    async def remove_by_id(self, id: UUID) -> Awaitable:
        await self.service.delete_by_id(id)

    async def update(self, domain: Translation) -> Awaitable:
        await self.service.update(domain)

    async def find_by_id(self, id: UUID) -> Awaitable[Translation]:
        result = await self.service.find_by_id(id)

        if result is None:
            raise RessourceNotFound()

        return result
