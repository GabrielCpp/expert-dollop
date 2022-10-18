from uuid import UUID
from expert_dollup.shared.database_services import Repository
from expert_dollup.shared.starlette_injection import IdProvider
from expert_dollup.core.domains import *


class AggregationUseCase:
    def __init__(self, repository: Repository[Aggregation], id_provider: IdProvider):
        self.repository = repository
        self.id_provider = id_provider

    async def find(self, project_definition_id: UUID, collection_id: UUID):
        return await self.repository.find_one_by(
            AggregateCollectionFilter(
                id=collection_id, project_definition_id=project_definition_id
            )
        )

    async def add(
        self,
        project_definition_id: UUID,
        new_aggregate_collection: NewAggregateCollection,
    ) -> AggregateCollection:
        aggregate_collection = AggregateCollection(
            id=self.id_provider.uuid4(),
            project_definition_id=project_definition_id,
            name=new_aggregate_collection.name,
            is_abstract=new_aggregate_collection.is_abstract,
            attributes_schema=new_aggregate_collection.attributes_schema,
        )
        await self.repository.insert(aggregate_collection)
        return aggregate_collection

    async def update(
        self,
        project_definition_id: UUID,
        collection_id: UUID,
        new_aggregate_collection: NewAggregateCollection,
    ) -> AggregateCollection:
        aggregate_collection = AggregateCollection(
            id=collection_id,
            project_definition_id=project_definition_id,
            name=new_aggregate_collection.name,
            is_abstract=new_aggregate_collection.is_abstract,
            attributes_schema=new_aggregate_collection.attributes_schema,
        )
        await self.repository.upserts([aggregate_collection])
        return aggregate_collection

    async def delete(self, project_definition_id: UUID, collection_id: UUID) -> None:
        await self.repository.delete_by(
            AggregateCollectionFilter(
                id=collection_id, project_definition_id=project_definition_id
            )
        )

    async def replace_aggregates(
        self,
        project_definition_id: UUID,
        collection_id: UUID,
        aggregates: List[Aggregate],
    ) -> None:
        pass

    async def get_aggregates(
        self, project_definition_id: UUID, collection_id: UUID
    ) -> List[Aggregate]:
        pass
