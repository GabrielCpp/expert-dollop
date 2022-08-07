from uuid import UUID
from expert_dollup.shared.database_services import CollectionService
from expert_dollup.core.domains import LabelCollection


class LabelCollectionUseCase:
    def __init__(self, label_collection_service: CollectionService[LabelCollection]):
        self.label_collection_service = label_collection_service

    async def find_by_id(self, id: UUID):
        return await self.label_collection_service.find_by_id(id)

    async def add(self, label_collection: LabelCollection) -> LabelCollection:
        await self.label_collection_service.insert(label_collection)
        return await self.label_collection_service.find_by_id(label_collection.id)

    async def update(self, label_collection: LabelCollection) -> LabelCollection:
        await self.label_collection_service.upserts([label_collection])
        return await self.label_collection_service.find_by_id(label_collection.id)

    async def delete_by_id(self, id: UUID) -> None:
        await self.label_collection_service.delete_by_id(id)
