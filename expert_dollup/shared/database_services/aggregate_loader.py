from typing import Type, TypeVar, List
from uuid import UUID
from .database_context import DatabaseContext, QueryFilter

T = TypeVar("T")


class AggregateLoader:
    def __init__(db_context: DatabaseContext):
        self.db_context = db_context
        self.cache = {}

    def reset_cache(self):
        self.cache = {}

    async def load(self, domain_type: Type[T], id: UUID) -> T:
        obj = self.cache.get(id)

        if obj is None:
            obj = await self.db_context.find_by_id(domain_type, id)
            self.cache[id] = obj

        return obj

    async def loads(
        self, pluck_filter_type: QueryFilter, domain_type: Type[T], ids: List[UUID]
    ) -> List[T]:
        objs = [None] * len(ids)
        not_founds = {}
        plucker = self.db_context.bind_query(Plucker)

        for index, id in enumerate(ids):
            obj = self.cache.get(id)

            if obj is None:
                not_founds[id] = index
            else:
                objs[index] = obj

        results = await plucker.plucks(lambda ids: pluck_filter_type(ids=ids))

        for obj in results:
            objs[not_founds[obj.id]] = obj

        return objs