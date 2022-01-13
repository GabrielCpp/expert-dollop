from typing import TypeVar, List, Optional, Union, Tuple, Literal
from inspect import isclass
from expert_dollup.shared.automapping import Mapper
from .query_filter import QueryFilter
from .page import Page
from .adapter_interfaces import (
    CollectionService,
    DbConnection,
    QueryBuilder,
)

Domain = TypeVar("Domain")
WhereFilter = Union[QueryFilter, QueryBuilder]
Id = TypeVar("Id")


class CollectionServiceProxy(CollectionService[Domain]):
    def __init__(self, database: DbConnection, mapper: Mapper):
        meta = self.__class__.Meta

        assert isclass(meta.dao), f"Meta of {__name__} must contain a dao type"
        assert isclass(meta.domain), f"Meta of {__name__} must contain a domain type"

        self._impl: CollectionService[Domain] = database.get_collection_service(
            meta, mapper
        )

    async def insert(self, domain: Domain):
        return await self._impl.insert(domain)

    async def insert_many(self, domains: List[Domain]):
        return await self._impl.insert_many(domains)

    async def upserts(self, domains: List[Domain]) -> None:
        await self._impl.upserts(domains)

    async def find_all(self, limit: int = 1000) -> List[Domain]:
        return await self._impl.find_all(limit)

    async def find_all_paginated(
        self, limit: int = 1000, next_page_token: Optional[str] = None
    ) -> Page[Domain]:
        return await self._impl.find_all_paginated(limit, next_page_token)

    async def find_by(self, query_filter: WhereFilter) -> List[Domain]:
        return await self._impl.find_by(query_filter)

    async def find_by_paginated(
        self,
        query_filter: WhereFilter,
        limit: int,
        next_page_token: Optional[str] = None,
    ) -> Page[Domain]:
        return await self._impl.find_by_paginated(query_filter, limit, next_page_token)

    async def find_one_by(self, query_filter: WhereFilter) -> Domain:
        return await self._impl.find_one_by(query_filter)

    async def find_by_id(self, pk_id: Id) -> Domain:
        return await self._impl.find_by_id(pk_id)

    async def delete_by(self, query_filter: WhereFilter):
        return await self._impl.delete_by(query_filter)

    async def delete_by_id(self, pk_id: Id):
        return await self._impl.delete_by_id(pk_id)

    async def update(self, value_filter: QueryFilter, query_filter: WhereFilter):
        return await self._impl.update(value_filter, query_filter)

    async def has(self, pk_id: Id) -> bool:
        return await self._impl.has(pk_id)

    async def count(self, query_filter: Optional[WhereFilter] = None) -> int:
        return await self._impl.count(query_filter)

    def make_record_token(self, domain: Domain) -> str:
        return self._impl.make_record_token(domain)

    def get_builder(self) -> QueryBuilder:
        return self._impl.get_builder()

    async def fetch_all_records(self, builder: QueryBuilder) -> dict:
        return await self._impl.fetch_all_records(builder)