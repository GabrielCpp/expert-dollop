from typing import Callable, TypeVar, List, Optional, Union, Type, Dict, Any
from typing_extensions import TypeAlias
from inspect import isclass
from expert_dollup.shared.automapping import Mapper
from .query_filter import QueryFilter
from .adapter_interfaces import (
    Repository,
    InternalRepository,
    DbConnection,
    QueryBuilder,
)

Domain = TypeVar("Domain")
WhereFilter: TypeAlias = Union[QueryFilter, QueryBuilder]
Id = TypeVar("Id")


class RepositoryProxy(Repository[Domain]):
    def __init__(self, repository: InternalRepository[Domain]):
        self._impl = repository

    @property
    def domain(self) -> Type:
        return self._impl.domain

    @property
    def batch_size(self) -> int:
        return self._impl.batch_size

    @property
    def db(self) -> DbConnection:
        return self._impl.db

    async def insert(self, domain: Domain):
        return await self._impl.insert(domain)

    async def inserts(self, domains: List[Domain]):
        return await self._impl.inserts(domains)

    async def upserts(self, domains: List[Domain]) -> None:
        await self._impl.upserts(domains)

    async def all(self, limit: int = 1000) -> List[Domain]:
        return await self._impl.all(limit)

    async def find_by(self, query_filter: WhereFilter) -> List[Domain]:
        return await self._impl.find_by(query_filter)

    async def find_one_by(self, query_filter: WhereFilter) -> Domain:
        return await self._impl.find_one_by(query_filter)

    async def find(self, pk_id: Id) -> Domain:
        return await self._impl.find(pk_id)

    async def delete_by(self, query_filter: WhereFilter):
        return await self._impl.delete_by(query_filter)

    async def delete(self, pk_id: Id):
        return await self._impl.delete(pk_id)

    async def update(self, value_filter: QueryFilter, query_filter: WhereFilter):
        return await self._impl.update(value_filter, query_filter)

    async def has(self, pk_id: Id) -> bool:
        return await self._impl.has(pk_id)

    async def exists(self, query_filter: WhereFilter) -> bool:
        return await self._impl.exists(query_filter)

    async def count(self, query_filter: Optional[WhereFilter] = None) -> int:
        return await self._impl.count(query_filter)

    async def execute(self, builder: WhereFilter) -> Union[Domain, List[Domain], None]:
        return await self._impl.execute(builder)
