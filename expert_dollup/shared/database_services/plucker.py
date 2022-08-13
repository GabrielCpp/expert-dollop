from abc import ABC, abstractmethod
from typing import Callable, List, TypeVar, Sequence, Generic
from uuid import UUID
from expert_dollup.shared.database_services import QueryFilter

Domain = TypeVar("Domain")


class Plucker(ABC, Generic[Domain]):
    @abstractmethod
    async def plucks(
        self,
        build_pluck_filter: Callable[[Sequence[UUID]], QueryFilter],
        ids_lists: Sequence[UUID],
    ) -> List[Domain]:
        pass

    @abstractmethod
    async def pluck_subressources(
        self,
        ressource_filter: QueryFilter,
        build_pluck_filter: Callable[[Sequence[UUID]], QueryFilter],
        ids_lists: Sequence[UUID],
    ) -> List[Domain]:
        pass
