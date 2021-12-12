from abc import ABC, abstractmethod
from typing import AsyncGenerator, TypeVar, List, Generic
from uuid import UUID
from expert_dollup.shared.database_services import QueryFilter

Domain = TypeVar("Domain")
Service = TypeVar("Service")


class Plucker(ABC, Generic[Service]):
    @abstractmethod
    async def pluck_batches(
        self, build_pluck_filter: QueryFilter, *ids_lists: List[List[UUID]]
    ) -> AsyncGenerator[List[Domain], None]:
        pass

    @abstractmethod
    async def plucks(
        self, build_pluck_filter: QueryFilter, *ids_lists: List[List[UUID]]
    ) -> List[Domain]:
        pass
