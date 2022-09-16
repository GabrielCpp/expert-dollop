from typing import Callable, Optional, TypeVar, Sequence, List
from uuid import UUID
from .adapter_interfaces import QueryFilter, InternalRepository
from .batch_helper import batch
from .plucker import Plucker


Domain = TypeVar("Domain")


class PluckQuery(Plucker[Domain]):
    def __init__(self, repository: InternalRepository[Domain]):
        self._repository = repository
        self._batch_size = 10

    async def plucks(
        self,
        build_pluck_filter: Callable[[Sequence[UUID]], QueryFilter],
        ids: Sequence[UUID],
    ) -> List[Domain]:
        all_results = []

        async for batch_results in self._pluck_by_batch(ids, build_pluck_filter):
            all_results.extend(batch_results)

        return all_results

    async def pluck_subressources(
        self,
        ressource_filter: QueryFilter,
        build_pluck_filter: Callable[[Sequence[UUID]], QueryFilter],
        ids: Sequence[UUID],
    ) -> List[Domain]:

        all_results = []

        async for batch_results in self._pluck_by_batch(
            ids, build_pluck_filter, ressource_filter
        ):
            all_results.extend(batch_results)

        return all_results

    async def _pluck_by_batch(
        self,
        ids: List[UUID],
        build_pluck_filter: Callable[[list], QueryFilter],
        ressource_filter: Optional[QueryFilter] = None,
    ):
        ressource_dict = {}

        if not ressource_filter is None:
            ressource_dict = self._repository.unpack_query(ressource_filter)

        for ids_batch in batch(ids, self._batch_size):
            pluck_filter = build_pluck_filter(ids_batch)
            pluck_filter_dict = self._repository.unpack_query(pluck_filter)

            query = self._repository.get_builder()

            for name, value in ressource_dict.items():
                query = query.where(name, "==", value)

            for name, values in pluck_filter_dict.items():
                query = query.where(name, "in", values)

            results = await self._repository.find_by(query)
            yield results
