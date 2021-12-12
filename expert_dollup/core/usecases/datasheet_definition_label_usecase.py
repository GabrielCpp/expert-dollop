from uuid import UUID
from typing import Awaitable
from expert_dollup.infra.services import LabelService
from expert_dollup.core.domains import Label


class LabelUseCase:
    def __init__(self, label_service: LabelService):
        self.label_service = label_service

    async def find_by_id(self, id: UUID):
        return await self.label_service.find_by_id(id)

    async def add(self, label: Label) -> Label:
        await self.label_service.insert(label)
        return await self.label_service.find_by_id(label.id)

    async def update(self, label: Label) -> Label:
        await self.label_service.update(label)
        return await self.label_service.find_by_id(label.id)

    async def delete_by_id(self, id: UUID):
        await self.label_service.delete_by_id(id)
