from typing import TypeVar, List
from uuid import UUID
from expert_dollup.core.queries import Plucker
from expert_dollup.shared.database_services import QueryFilter, CollectionService
from expert_dollup.shared.database_services import QueryBuilder

Domain = TypeVar("Domain")


class PluckQuery(Plucker):
    @staticmethod
    def batch(iterable, n):
        current_batch = []

        for item in iterable:
            current_batch.append(item)
            if len(current_batch) == n:
                yield current_batch
                current_batch = []

        if current_batch:
            yield current_batch

    def __init__(self, service: CollectionService[Domain]):
        self.service = service
        self.batch_size = 1000

    async def pluck_batches(
        self, build_pluck_filter: QueryFilter, *ids_lists: List[UUID]
    ) -> List[Domain]:

        for args in zip(*[PluckQuery.batch(ids, self.batch_size) for ids in ids_lists]):
            builder = self.service.get_builder()
            pluck_filter = build_pluck_filter(*args)
            query = builder.pluck(pluck_filter).finalize()
            results = await self.service.find_by(query)
            yield results

    async def plucks(self, build_pluck_filter: QueryFilter, *ids_lists: List[UUID]):
        all_results = []

        async for batch_results in self.pluck_batches(build_pluck_filter, *ids_lists):
            all_results.extend(batch_results)

        return all_results

    async def pluck_subressources(
        self,
        ressource_filter: QueryFilter,
        build_pluck_filter: QueryFilter,
        *ids_lists: List[List[UUID]]
    ) -> List[Domain]:
        builder = self.service.get_builder().find_by(ressource_filter)
        all_results = []

        async for batch_results in self._pluck_by_batch(
            builder, build_pluck_filter, *ids_lists
        ):
            all_results.extend(batch_results)

        return all_results

    async def _pluck_by_batch(
        self,
        builder: QueryBuilder,
        build_pluck_filter: QueryFilter,
        *ids_lists: List[List[UUID]]
    ):
        for args in zip(*[PluckQuery.batch(ids, self.batch_size) for ids in ids_lists]):

            pluck_filter = build_pluck_filter(*args)
            query = builder.pluck(pluck_filter).finalize()
            results = await self.service.find_by(query)
            yield results
