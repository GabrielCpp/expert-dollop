from abc import ABC, abstractmethod
from typing import Callable, Iterable, TypeVar, List, Generic
from uuid import UUID
from expert_dollup.shared.database_services import QueryFilter
from mypy_extensions import VarArg

Domain = TypeVar("Domain")


class Plucker(ABC, Generic[Domain]):
    @abstractmethod
    async def plucks(
        self,
        build_pluck_filter: Callable[[VarArg(UUID)], QueryFilter],
        *ids_lists: List[Iterable[UUID]]
    ) -> List[Domain]:
        pass

    @abstractmethod
    async def pluck_subressources(
        self,
        ressource_filter: QueryFilter,
        build_pluck_filter: Callable[[VarArg(UUID)], QueryFilter],
        *ids_lists: List[Iterable[UUID]]
    ) -> List[Domain]:
        pass
