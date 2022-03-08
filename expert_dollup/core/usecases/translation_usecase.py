from typing import Optional, List
from itertools import chain
from expert_dollup.shared.database_services import Page, Paginator, CollectionService
from expert_dollup.core.exceptions import RessourceNotFound, ValidationError
from expert_dollup.core.domains import (
    Translation,
    TranslationId,
    TranslationRessourceLocaleQuery,
    ProjectDetails,
    Ressource,
    Datasheet,
    RessourceFilter,
    RessourceId,
    User,
)


class TranslationUseCase:
    def __init__(
        self,
        service: CollectionService[Translation],
        translation_paginator: Paginator[Translation],
        ressource_service: CollectionService[Ressource],
        project_details_service: CollectionService[ProjectDetails],
        datasheet_service: CollectionService[Datasheet],
    ):
        self.service = service
        self.translation_paginator = translation_paginator
        self.ressource_service = ressource_service
        self.project_details_service = project_details_service
        self.datasheet_service = datasheet_service

    async def add(self, domain: Translation):
        if not await self.ressource_service.exists(
            RessourceFilter(id=domain.ressource_id)
        ):
            raise ValidationError.for_field(
                "ressource_id", "Missing an attached ressource"
            )

        await self.service.insert(domain)
        return domain

    async def delete_by_id(self, id: TranslationId):
        await self.service.delete_by_id(id)

    async def update(self, domain: Translation):
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

    async def find_by_id(self, id: TranslationId) -> Translation:
        result = await self.service.find_by_id(id)

        if result is None:
            raise RessourceNotFound()

        return result

    async def find_by_ressource_locale(
        self,
        query: TranslationRessourceLocaleQuery,
        limit: int,
        next_page_token: Optional[str],
    ) -> Page[Translation]:
        return await self.translation_paginator.find_page(
            query,
            limit,
            next_page_token,
        )

    async def get_translation_bundle(
        self, query: TranslationRessourceLocaleQuery, user: User
    ) -> List[Translation]:
        if query.locale == "en":
            query.locale = "en_US"

        if query.locale == "fr":
            query.locale = "fr_CA"

        ressource = await self.ressource_service.find_by_id(
            RessourceId(id=query.ressource_id, user_id=user.id)
        )

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
                    ressource_id=datasheet.project_definition_id,
                    locale=query.locale,
                )
            )

            return chain(datasheet_translations, project_def_translations)

        return await self.service.find_by(query)
