from uuid import UUID
from typing import Awaitable
from expert_dollup.infra.services import LabelCollectionService
from expert_dollup.core.domains import LabelCollection


class LabelCollectionUseCase:
    def __init__(self, label_collection_service: LabelCollectionService):
        self.label_collection_service = label_collection_service

    async def find_by_id(self, id: UUID):
        return await self.label_collection_service.find_by_id(id)

    async def add(
        self, label_collection: LabelCollection
    ) -> Awaitable[LabelCollection]:
        await self.label_collection_service.insert(label_collection)
        return await self.label_collection_service.find_by_id(label_collection.id)

    async def update(
        self, label_collection: LabelCollection
    ) -> Awaitable[LabelCollection]:
        await self.label_collection_service.update(label_collection)
        return await self.label_collection_service.find_by_id(label_collection.id)

    async def delete_by_id(self, id: UUID) -> Awaitable[LabelCollection]:
        await self.label_collection_service.delete_by_id(id)