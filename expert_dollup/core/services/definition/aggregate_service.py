from uuid import UUID
from typing import List
from expert_dollup.shared.database_services import *
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.domains import *
from expert_dollup.shared.validation import ValidationError


@dataclass
class AggregateBuilder(ObjectFactory):
    id_provider: IdProvider
    clock: Clock

    def add_aggregate(
        self,
        project_definition_id: UUID,
        collection_id: UUID,
        new_aggregate: NewAggregate,
    ) -> None:
        self.aggregate = Aggregate(
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

    def add_replacement(
        self,
        project_definition_id: UUID,
        collection_id: UUID,
        aggregate_id: UUID,
        new_aggregate: NewAggregate,
    ) -> None:
        self.aggregate = Aggregate(
            id=aggregate_id,
            project_definition_id=project_definition_id,
            collection_id=collection_id,
            ordinal=new_aggregate.ordinal,
            name=new_aggregate.name,
            is_extendable=new_aggregate.is_extendable,
            attributes={
                attribute.name: attribute for attribute in new_aggregate.attributes
            },
        )

    def add_translations(self, new_translations: List[NewTranslation]) -> None:
        self.translations = [
            Translation(
                ressource_id=self.aggregate.project_definition_id,
                locale=new_translation.locale,
                scope=self.aggregate.id,
                name=new_translation.name,
                value=new_translation.value,
                creation_date_utc=self.clock.utcnow(),
            )
            for new_translation in new_translations
        ]

    def build(self) -> LocalizedAggregate:
        return LocalizedAggregate(
            aggregate=self.aggregate, translations=self.translations
        )


class AggregateService:
    def __init__(self, db_context: DatabaseContext, instanciate: Instanciator):
        self.db_context = db_context
        self.instanciate = instanciate

    async def create(
        self,
        project_definition_id: UUID,
        collection_id: UUID,
        new_aggregate: NewAggregate,
    ) -> Aggregate:
        builder: AggregateBuilder = self.instanciate(AggregateBuilder)
        builder.add_aggregate(project_definition_id, collection_id, new_aggregate)
        builder.add_translations(new_aggregate.translated)
        localized_aggregate = builder.build()

        await localized_aggregate.validate()
        await self.db_context.insert(Aggregate, localized_aggregate.aggregate)
        await self.db_context.upserts(Translation, localized_aggregate.translations)

        return localized_aggregate.aggregate

    async def update(
        self,
        project_definition_id: UUID,
        collection_id: UUID,
        aggregate_id: UUID,
        replacement: NewAggregate,
    ) -> Aggregate:
        builder: AggregateBuilder = self.instanciate(AggregateBuilder)
        builder.add_replacement(
            project_definition_id, collection_id, aggregate_id, replacement
        )
        builder.add_translations(replacement.translated)
        localized_aggregate = builder.build()

        await localized_aggregate.validate()
        await self.db_context.upserts(Aggregate, [localized_aggregate.aggregate])
        await self.db_context.upserts(Translation, localized_aggregate.translations)

        return localized_aggregate.aggregate
