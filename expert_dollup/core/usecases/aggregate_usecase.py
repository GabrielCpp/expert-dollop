from uuid import UUID
from typing import List
from expert_dollup.shared.database_services import *
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.domains import *
from .translation_usecase import TranslationUseCase


class AggregateUseCase:
    def __init__(
        self,
        db_context: DatabaseContext,
        id_provider: IdProvider,
        clock: Clock,
    ):
        self.db_context = db_context
        self.id_provider = id_provider
        self.clock = clock

    async def create(
        self,
        project_definition_id: UUID,
        collection_id: UUID,
        new_aggregate: NewAggregate,
    ) -> Aggregate:
        aggregate = Aggregate(
            id=self.id_provider.uuid4(),
            project_definition_id=project_definition_id,
            collection_id=collection_id,
            ordinal=new_aggregate.ordinal,
            name=new_aggregate.name,
            is_extendable=new_aggregate.is_extendable,
            attributes={
                attribute.name: attribute for attribute in new_aggregate.attributes
            },
        )
        await self.db_context.insert(Aggregate, aggregate)
        await self.upsert_translations(
            project_definition_id, aggregate.id, new_aggregate.translated
        )

        return aggregate

    async def update(
        self,
        project_definition_id: UUID,
        collection_id: UUID,
        aggregate_id: UUID,
        replacement: NewAggregate,
    ) -> Aggregate:
        aggregate = Aggregate(
            id=aggregate_id,
            project_definition_id=project_definition_id,
            collection_id=collection_id,
            ordinal=replacement.ordinal,
            name=replacement.name,
            is_extendable=replacement.is_extendable,
            attributes={
                attribute.name: attribute for attribute in replacement.attributes
            },
        )
        await self.db_context.upserts(Aggregate, [aggregate])
        await self.upsert_translations(
            project_definition_id, aggregate_id, replacement.translated
        )
        return aggregate

    async def upsert_translations(
        self,
        ressource_id: UUID,
        scope: UUID,
        new_translations: List[NewTranslation],
    ):
        translations = [
            Translation(
                ressource_id=ressource_id,
                locale=new_translation.locale,
                scope=scope,
                name=new_translation.name,
                value=new_translation.value,
                creation_date_utc=self.clock.utcnow(),
            )
            for new_translation in new_translations
        ]

        await self.db_context.upserts(Translation, translations)
