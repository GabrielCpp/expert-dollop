from typing import Callable, Optional, TypeVar, List
from uuid import UUID
from expert_dollup.shared.automapping import Mapper
from .adapter_interfaces import QueryFilter, CollectionService
from .batch_helper import batch
from .plucker import Plucker


Domain = TypeVar("Domain")


class PluckQuery(Plucker[Domain]):
    def __init__(self, service: CollectionService[Domain], mapper: Mapper):
        self.service = service
        self.batch_size = 10
        self.mapper = mapper

    async def plucks(
        self, build_pluck_filter: Callable[[list], QueryFilter], ids: List[UUID]
    ):
        all_results = []

        async for batch_results in self._pluck_by_batch(ids, build_pluck_filter):
            all_results.extend(batch_results)

        return all_results

    async def pluck_subressources(
        self,
        ressource_filter: QueryFilter,
        build_pluck_filter: Callable[[list], QueryFilter],
        ids: List[UUID],
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
            ressource_dict = self.mapper.map(
                ressource_filter, dict, ressource_filter.__class__
            )

        for ids_batch in batch(ids, self.batch_size):
            pluck_filter = build_pluck_filter(ids_batch)
            pluck_filter_dict = self.mapper.map(
                pluck_filter, dict, pluck_filter.__class__
            )

            query = self.service.get_builder()

            for name, value in ressource_dict.items():
                query = query.where(name, "==", value)

            for name, values in pluck_filter_dict.items():
                query = query.where(name, "in", values)

            results = await self.service.find_by(query)
            yield results
