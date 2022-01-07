from typing import Awaitable, Optional, List
from itertools import chain
from expert_dollup.core.exceptions import RessourceNotFound, ValidationError
from expert_dollup.core.domains import (
    Translation,
    TranslationId,
    TranslationRessourceLocaleQuery,
)
from expert_dollup.infra.services import (
    TranslationService,
    RessourceService,
    ProjectService,
    DatasheetService,
)
from expert_dollup.shared.database_services import Page


class TranslationUseCase:
    def __init__(
        self,
        service: TranslationService,
        ressource_service: RessourceService,
        project_details_service: ProjectService,
        datasheet_service: DatasheetService,
    ):
        self.service = service
        self.ressource_service = ressource_service
        self.project_details_service = project_details_service
        self.datasheet_service = datasheet_service

    async def add(self, domain: Translation) -> Awaitable:
        if not await self.ressource_service.has(domain.ressource_id):
            raise ValidationError.for_field(
                "ressource_id", "Missing an attached ressource"
            )

        await self.service.insert(domain)
        return domain

    async def delete_by_id(self, id: TranslationId) -> Awaitable:
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
                scope=domain.scope,
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

    async def get_translation_bundle(
        self, query: TranslationRessourceLocaleQuery
    ) -> List[Translation]:
        if query.locale == "en":
            query.locale = "en_US"

        if query.locale == "fr":
            query.locale = "fr_CA"

        ressource = await self.ressource_service.find_by_id(query.ressource_id)

        if ressource.kind == "project":
            project_details = await self.project_details_service.find_by_id(
                query.ressource_id
            )
            datasheet = await self.datasheet_service.find_by_id(
                project_details.datasheet_id
            )

            project_def_translations = await self.service.find_by(
                TranslationRessourceLocaleQuery(
                    ressource_id=project_details.project_def_id,
                    locale=query.locale,
                )
            )

            datasheet_translations = await self.service.find_by(
                TranslationRessourceLocaleQuery(
                    ressource_id=datasheet.datasheet_def_id,
                    locale=query.locale,
                )
            )

            return chain(datasheet_translations, project_def_translations)

        return await self.service.find_by(query)
