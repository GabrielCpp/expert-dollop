from typing import Iterable, Optional
from itertools import chain
from uuid import UUID
from expert_dollup.shared.database_services import *
from expert_dollup.shared.starlette_injection import Clock, IdProvider
from expert_dollup.core.exceptions import RessourceNotFound
from expert_dollup.shared.validation import ValidationError
from expert_dollup.core.domains import *


class TranslationUseCase:
    def __init__(
        self,
        db_context: DatabaseContext,
        clock: Clock,
        id_provider: IdProvider,
    ):
        self.db_context = db_context
        self.clock = clock
        self.id_provider = id_provider

    async def find(
        self,
        ressource_id: UUID,
        locale: str,
        name: str,
    ) -> Translation:
        return await self.db_context.find(
            Translation, TranslationId(ressource_id, locale, name)
        )

    async def add(self, definition_id: UUID, new_translation: NewTranslation):
        domain = Translation(
            definition_id,
            new_translation.locale,
            new_translation.scope,
            new_translation.name,
            new_translation.value,
            self.clock.utcnow(),
        )
        await self.db_context.insert(
            Translation,
            domain,
        )
        return domain

    async def update(self, definition_id: UUID, replacement: NewTranslation):
        domain = Translation(
            definition_id,
            replacement.locale,
            replacement.scope,
            replacement.name,
            replacement.value,
            self.clock.utcnow(),
        )
        await self.db_context.upserts(
            Translation,
            [domain],
        )
        return domain

    async def delete(
        self,
        ressource_id: UUID,
        locale: str,
        name: str,
    ):
        await self.db_context.delete(
            Translation, TranslationId(ressource_id, locale, name)
        )

    async def get_translation_bundle(
        self, ressource_id: UUID, locale: str, user: User
    ) -> Iterable[Translation]:
        if locale == "en":
            locale = "en-US"

        if locale == "fr":
            locale = "fr-CA"

        ressource = await self.db_context.find(
            Ressource,
            RessourceId(id=ressource_id, organization_id=user.organization_id),
        )

        if ressource.kind == "project":
            project_details = await self.db_context.find(ProjectDetails, ressource_id)
            datasheet = await self.db_context.find(
                Datasheet, project_details.datasheet_id
            )

            project_def_translations = await self.db_context.find_by(
                Translation,
                TranslationFilter(
                    ressource_id=project_details.project_definition_id,
                    locale=locale,
                ),
            )

            datasheet_translations = await self.db_context.find_by(
                Translation,
                TranslationFilter(
                    ressource_id=datasheet.project_definition_id,
                    locale=locale,
                ),
            )

            return chain(datasheet_translations, project_def_translations)

        return await self.db_context.find_by(
            Translation, TranslationFilter(ressource_id=ressource_id, locale=locale)
        )
