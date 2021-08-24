from typing import Awaitable, Optional
from expert_dollup.core.exceptions import RessourceNotFound, ValidationError
from expert_dollup.core.domains import (
    Translation,
    TranslationId,
    Ressource,
    TranslationRessourceLocaleQuery,
)
from expert_dollup.infra.services import TranslationService, RessourceService
from expert_dollup.shared.database_services import Page


class TranslationUseCase:
    def __init__(
        self, service: TranslationService, ressource_service: RessourceService
    ):
        self.service = service
        self.ressource_service = ressource_service

    async def add(self, domain: Translation) -> Awaitable:
        if not await self.ressource_service.has(domain.ressource_id):
            raise ValidationError.for_field(
                "ressource_id", "Missing an attached ressource"
            )

        await self.service.insert(domain)
        return domain

    async def remove_by_id(self, id: TranslationId) -> Awaitable:
        await self.service.delete_by_id(id)

    async def update(self, domain: Translation) -> Awaitable:
        if not await self.ressource_service.has(domain.ressource_id):
            raise ValidationError.for_field(
                "ressource_id", "Missing an attached ressource"
            )

        await self.service.update(domain)
        return await self.find_by_id(
            TranslationId(
                ressource_id=domain.ressource_id,
                scope=scope,
                locale=domain.locale,
                name=domain.name,
            )
        )

    async def find_by_id(self, id: TranslationId) -> Awaitable[Translation]:
        result = await self.service.find_by_id(id)

        if result is None:
            raise RessourceNotFound()

        return result

    async def find_by_ressource_locale(
        self,
        query: TranslationRessourceLocaleQuery,
        limit: int,
        next_page_token: Optional[str],
    ) -> Awaitable[Page[Translation]]:
        return await self.service.find_by_paginated(
            query,
            limit,
            next_page_token,
        )
