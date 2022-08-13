from typing import Type, TypeVar, List, Any, Optional, Type
from injector import Injector
from .database_context import DatabaseContext
from .adapter_interfaces import CollectionService, WhereFilter, QueryFilter

Domain = TypeVar("Domain")
Query = TypeVar("Query")
Id = TypeVar("Id")


class DatabaseContextMultiplexer(DatabaseContext):
    def __init__(self, injector: Injector, databases: List[Type]):
        self.injector = injector
        self.databases = [injector.get(db_type) for db_type in databases]
        self.repositories: Dict[Type, CollectionService[Any]] = {}

    def get_repository(self, domain_type: Type[Domain]) -> CollectionService[Domain]:
        collection_service = self.repositories.get(domain_type)

        if collection_service is None:
            collection_service = self.injector.get(CollectionService[domain_type])
            self.repositories[domain_type] = collection_service

        return collection_service

    def bind_query(self, query_type: Type[Query]) -> Query:
        return self.injector.get(query_type)

    async def insert(self, domain_type: Type[Domain], domain: Domain):
        return await self.get_repository(domain_type).insert(domain)

    async def insert_many(self, domain_type: Type[Domain], domains: List[Domain]):
        return await self.get_repository(domain_type).insert_many(domains)

    async def upserts(self, domain_type: Type[Domain], domains: List[Domain]) -> None:
        return await self.get_repository(domain_type).upserts(domains)

    async def find_all(
        self, domain_type: Type[Domain], limit: int = 1000
    ) -> List[Domain]:
        return await self.get_repository(domain_type).find_all(limit)

    async def find_by(
        self, domain_type: Type[Domain], query_filter: WhereFilter
    ) -> List[Domain]:
        return await self.get_repository(domain_type).find_by(query_filter)

    async def find_one_by(
        self, domain_type: Type[Domain], query_filter: WhereFilter
    ) -> Domain:
        return await self.get_repository(domain_type).find_one_by(query_filter)

    async def find_by_id(self, domain_type: Type[Domain], pk_id: Id) -> Domain:
        return await self.get_repository(domain_type).find_by_id(pk_id)

    async def delete_by(self, domain_type: Type[Domain], query_filter: WhereFilter):
        return await self.get_repository(domain_type).delete_by(query_filter)

    async def delete_by_id(self, domain_type: Type[Domain], pk_id: Id):
        return await self.get_repository(domain_type).delete_by_id(pk_id)

    async def update(
        self,
        domain_type: Type[Domain],
        value_filter: QueryFilter,
        query_filter: WhereFilter,
    ):
        return await self.get_repository(domain_type).update(
            domain_type, value_filter, query_filter
        )

    async def has(self, domain_type: Type[Domain], pk_id: Id) -> bool:
        return await self.get_repository(domain_type).has(pk_id)

    async def exists(
        self, domain_type: Type[Domain], query_filter: WhereFilter
    ) -> bool:
        return await self.get_repository(domain_type).has(query_filter)

    async def count(
        self, domain_type: Type[Domain], query_filter: Optional[WhereFilter] = None
    ) -> int:
        return await self.get_repository(domain_type).has(query_filter)
