from typing import List, TypeVar, Optional, Awaitable, Dict, Type, Tuple, Union, Set
from google.cloud.firestore import AsyncClient
from google.cloud.firestore_v1 import Increment
from google.auth.credentials import AnonymousCredentials
from expert_dollup.shared.automapping import Mapper
from ..page import Page
from ..query_filter import QueryFilter
from ..exceptions import RecordNotFound
from ..batch_helper import batch
from ..json_serializer import JsonSerializer
from ..adapter_interfaces import (
    CollectionService,
    QueryBuilder,
    WhereFilter,
    DbConnection,
)


class FirestoreConnection(DbConnection):
    def __init__(self, connection_string: str, **kwargs):
        self.connection_string = connection_string
        self._database = AsyncClient(
            project="my-project", credentials=AnonymousCredentials()
        )
        self.tables: Set[Type] = set()

    def get_collection_service(self, meta: Type, mapper: Mapper):
        return FirestoreTableService(meta, self.tables, self._database, mapper)

    def load_metadatas(self, dao_types):
        self.tables = set(dao_types)

    async def truncate_db(self, tables: Optional[List[str]] = None):
        pass

    async def drop_db(self):
        pass

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    @property
    def is_connected(self) -> bool:
        pass


Domain = TypeVar("Domain")
Id = TypeVar("Id")


class FirestoreTableService(CollectionService[Domain]):
    def __init__(
        self,
        meta: Type,
        tables: Set[Type],
        connector: AsyncClient,
        mapper: Mapper,
    ):
        self._mapper = mapper
        self._database = connector
        self._dao = meta.dao
        self._domain = meta.domain

    async def insert(self, domain: Domain):
        pass

    async def insert_many(self, domains: List[Domain]):
        pass

    async def update(self, value_filter: QueryFilter, query_filter: WhereFilter):
        pass

    async def upserts(self, domains: List[Domain]) -> None:
        pass

    async def find_all(self, limit: int = 1000) -> List[Domain]:
        pass

    async def find_all_paginated(
        self, limit: int = 1000, next_page_token: Optional[str] = None
    ) -> Page[Domain]:
        pass

    async def find_by(self, query_filter: WhereFilter) -> List[Domain]:
        pass

    async def find_by_paginated(
        self,
        query_filter: WhereFilter,
        limit: int,
        next_page_token: Optional[str] = None,
    ) -> Page[Domain]:
        pass

    async def find_one_by(self, query_filter: WhereFilter) -> Domain:
        pass

    async def find_by_id(self, pk_id: Id) -> Domain:
        pass

    async def has(self, pk_id: Id) -> bool:
        pass

    async def count(self, query_filter: Optional[WhereFilter] = None) -> int:
        pass

    async def delete_by(self, query_filter: WhereFilter):
        pass

    async def delete_by_id(self, pk_id: Id):
        pass

    def get_builder(self) -> QueryBuilder:
        return PostgresQueryBuilder(self._table, self._mapper, self._build_filter)

    def make_record_token(self, domain: Domain) -> str:
        assert not self._paginator is None, "Paginator required"
        dao = self._mapper.map(domain, self._dao)
        next_page_token = self._paginator.encode_dao(dao)
        return next_page_token