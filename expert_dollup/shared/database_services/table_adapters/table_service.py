from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Awaitable, List, Optional, Union
from ..page import Page
from ..query_filter import QueryFilter

Domain = TypeVar("Domain")
Id = TypeVar("Id")


class QueryBuilder(ABC):
    @abstractmethod
    def select_fields(self, *names: List[str]) -> "QueryBuilder":
        pass

    @abstractmethod
    def find_by(self, query_filter: QueryFilter) -> "QueryBuilder":
        pass

    @abstractmethod
    def startwiths(self, query_filter: QueryFilter) -> "QueryBuilder":
        pass

    @abstractmethod
    def pluck(self, query_filter: QueryFilter) -> "QueryBuilder":
        pass

    @abstractmethod
    def save(self, name: str) -> "QueryBuilder":
        pass

    @abstractmethod
    def any_of(self, *names: List[str]) -> "QueryBuilder":
        pass

    @abstractmethod
    def all_of(self, *names: List[str]) -> "QueryBuilder":
        pass

    @abstractmethod
    def finalize(self) -> "QueryBuilder":
        pass


WhereFilter = Union[QueryFilter, QueryBuilder]


class TableService(ABC, Generic[Domain]):
    @abstractmethod
    async def insert(self, domain: Domain) -> Awaitable:
        pass

    @abstractmethod
    async def insert_many(self, domains: List[Domain]) -> Awaitable:
        pass

    @abstractmethod
    async def find_all(self, limit: int = 1000) -> Awaitable[List[Domain]]:
        pass

    @abstractmethod
    async def find_all_paginated(
        self, limit: int = 1000, next_page_token: Optional[str] = None
    ) -> Awaitable[Page[Domain]]:
        pass

    @abstractmethod
    async def find_by(
        self,
        query_filter: WhereFilter,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Awaitable[List[Domain]]:
        pass

    @abstractmethod
    async def find_by_paginated(
        self,
        query_filter: WhereFilter,
        limit: int,
        next_page_token: Optional[str] = None,
    ) -> Awaitable[Page[Domain]]:
        pass

    @abstractmethod
    async def find_one_by(self, query_filter: WhereFilter) -> Awaitable[List[Domain]]:
        pass

    @abstractmethod
    async def find_by_id(self, pk_id: Id) -> Awaitable[Domain]:
        pass

    @abstractmethod
    async def delete_by(self, query_filter: WhereFilter) -> Awaitable:
        pass

    @abstractmethod
    async def delete_by_id(self, pk_id: Id) -> Awaitable:
        pass

    @abstractmethod
    async def update(
        self, value_filter: QueryFilter, query_filter: WhereFilter
    ) -> Awaitable:
        """
        Update records base on query.
        """

    @abstractmethod
    async def has(self, pk_id: Id) -> Awaitable[bool]:
        pass

    @abstractmethod
    async def count(self, query_filter: Optional[WhereFilter] = None) -> Awaitable[int]:
        pass

    @abstractmethod
    def make_record_token(self, domain: Domain) -> str:
        """
        Return next page token for a domain object.
        """

    @abstractmethod
    def get_builder(self) -> QueryBuilder:
        """
        Return new query builder
        """

    async def fetch_all_records(self, builder: QueryBuilder) -> dict:
        pass