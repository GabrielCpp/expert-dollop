from abc import ABC, abstractmethod
from typing import Type, TypeVar, List, Optional, Union
from .adapter_interfaces import CollectionService, WhereFilter, QueryFilter

Domain = TypeVar("Domain")
Query = TypeVar("Query")
Id = TypeVar("Id")


class DatabaseContext(ABC):
    @abstractmethod
    def get_repository(self, domain_type: Type[Domain]) -> CollectionService[Domain]:
        pass

    @abstractmethod
    def bind_query(self, query_type: Union[ABC, Type[Query]]) -> Query:
        pass

    @abstractmethod
    async def insert(self, domain_type: Type[Domain], domain: Domain):
        pass

    @abstractmethod
    async def insert_many(self, domain_type: Type[Domain], domains: List[Domain]):
        pass

    @abstractmethod
    async def upserts(self, domain_type: Type[Domain], domains: List[Domain]) -> None:
        pass

    @abstractmethod
    async def find_all(
        self, domain_type: Type[Domain], limit: int = 1000
    ) -> List[Domain]:
        pass

    @abstractmethod
    async def find_by(
        self, domain_type: Type[Domain], query_filter: WhereFilter
    ) -> List[Domain]:
        pass

    @abstractmethod
    async def find_one_by(
        self, domain_type: Type[Domain], query_filter: WhereFilter
    ) -> Domain:
        pass

    @abstractmethod
    async def find_by_id(self, domain_type: Type[Domain], pk_id: Id) -> Domain:
        pass

    @abstractmethod
    async def delete_by(self, domain_type: Type[Domain], query_filter: WhereFilter):
        pass

    @abstractmethod
    async def delete_by_id(self, domain_type: Type[Domain], pk_id: Id):
        pass

    @abstractmethod
    async def update(
        self,
        domain_type: Type[Domain],
        value_filter: QueryFilter,
        query_filter: WhereFilter,
    ):
        pass

    @abstractmethod
    async def has(self, domain_type: Type[Domain], pk_id: Id) -> bool:
        pass

    @abstractmethod
    async def exists(
        self, domain_type: Type[Domain], query_filter: WhereFilter
    ) -> bool:
        pass

    @abstractmethod
    async def count(
        self, domain_type: Type[Domain], query_filter: Optional[WhereFilter] = None
    ) -> int:
        pass
