from abc import ABC, abstractmethod
from typing import Type, TypeVar, List, Optional, Union
from .adapter_interfaces import Repository, WhereFilter, QueryFilter

Domain = TypeVar("Domain")
Query = TypeVar("Query")
Id = TypeVar("Id")


class DatabaseContext(ABC):
    @abstractmethod
    def get_repository(self, domain_type: Type[Domain]) -> Repository[Domain]:
        pass

    @abstractmethod
    async def insert(self, domain_type: Type[Domain], domain: Domain):
        pass

    @abstractmethod
    async def inserts(self, domain_type: Type[Domain], domains: List[Domain]):
        pass

    @abstractmethod
    async def upserts(self, domain_type: Type[Domain], domains: List[Domain]) -> None:
        pass

    @abstractmethod
    async def all(self, domain_type: Type[Domain], limit: int = 1000) -> List[Domain]:
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
    async def find(self, domain_type: Type[Domain], pk_id: Id) -> Domain:
        pass

    @abstractmethod
    async def delete_by(self, domain_type: Type[Domain], query_filter: WhereFilter):
        pass

    @abstractmethod
    async def delete(self, domain_type: Type[Domain], pk_id: Id):
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

    @abstractmethod
    async def execute(
        self, domain_type: Type[Domain], builder: WhereFilter
    ) -> Union[Domain, List[Domain], None]:
        pass
