from os import environ
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Union, Type, Tuple, Literal
from inspect import isclass
from urllib.parse import urlparse
from pydantic import BaseModel
from expert_dollup.shared.automapping import Mapper
from .page import Page
from .query_filter import QueryFilter


class DbConnection(ABC):
    _REGISTRY = {}

    @abstractmethod
    def load_metadatas(self, dao_types):
        pass

    @abstractmethod
    def get_collection_service(self, meta: Type, mapper: Mapper):
        pass

    @abstractmethod
    async def truncate_db(self, tables: Optional[List[str]] = None):
        pass

    @abstractmethod
    async def drop_db(self):
        pass


class QueryBuilder(ABC):
    @abstractmethod
    def select(self, *names: List[str]) -> "QueryBuilder":
        pass

    @abstractmethod
    def limit(self, limit: int) -> "QueryBuilder":
        pass

    @abstractmethod
    def orderby(self, *orders) -> "QueryBuilder":
        pass

    @abstractmethod
    def where(self, *ops) -> "QueryBuilder":
        pass

    @abstractmethod
    def construct(self, name, *ops) -> "QueryBuilder":
        pass

    @abstractmethod
    def apply(self, builder: callable, *args, **kargs) -> "QueryBuilder":
        pass

    @abstractmethod
    def clone(self) -> "QueryBuilder":
        pass


Domain = TypeVar("Domain")
Id = TypeVar("Id")
WhereFilter = Union[QueryFilter, QueryBuilder]


class CollectionService(ABC, Generic[Domain]):
    @property
    @abstractmethod
    def domain(self) -> Type:
        pass

    @property
    @abstractmethod
    def dao(self) -> Type:
        pass

    @abstractmethod
    async def insert(self, domain: Domain):
        pass

    @abstractmethod
    async def insert_many(self, domains: List[Domain]):
        pass

    @abstractmethod
    async def upserts(self, domains: List[Domain]) -> None:
        pass

    @abstractmethod
    async def find_all(self, limit: int = 1000) -> List[Domain]:
        pass

    @abstractmethod
    async def find_by(self, query_filter: WhereFilter) -> List[Domain]:
        pass

    @abstractmethod
    async def find_one_by(self, query_filter: WhereFilter) -> Domain:
        pass

    @abstractmethod
    async def find_by_id(self, pk_id: Id) -> Domain:
        pass

    @abstractmethod
    async def delete_by(self, query_filter: WhereFilter):
        pass

    @abstractmethod
    async def delete_by_id(self, pk_id: Id):
        pass

    @abstractmethod
    async def update(self, value_filter: QueryFilter, query_filter: WhereFilter):
        """
        Update records base on query.
        """

    @abstractmethod
    async def has(self, pk_id: Id) -> bool:
        pass

    @abstractmethod
    async def count(self, query_filter: Optional[WhereFilter] = None) -> int:
        pass

    @abstractmethod
    def get_builder(self) -> QueryBuilder:
        """
        Return new query builder
        """

    @abstractmethod
    async def fetch_all_records(self, builder: QueryBuilder) -> dict:
        pass


class Paginator(ABC, Generic[Domain]):
    @abstractmethod
    async def find_page(
        self,
        builder: Optional[WhereFilter],
        limit: int,
        next_page_token: Optional[str] = None,
    ) -> Page[Domain]:
        pass

    @abstractmethod
    def make_record_token(self, domain: Domain) -> str:
        pass


def create_connection(
    connection_string: str, dao_module=None, **kwargs
) -> DbConnection:
    scheme = urlparse(connection_string).scheme

    if len(DbConnection._REGISTRY) == 0:
        connectors = environ.get("DB_CONNECTORS", "postgresql+asyncpg").split()

        for connector in connectors:
            if connector == "postgresql+asyncpg":
                from .database_adapters.postgres_adapter import PostgresConnection

                DbConnection._REGISTRY["postgresql+asyncpg"] = PostgresConnection

    build_connection = DbConnection._REGISTRY.get(scheme)

    if build_connection is None:
        raise KeyError(f"No key for schem {scheme}")

    connection = build_connection(connection_string, **kwargs)

    if not dao_module is None:
        connection.load_metadatas(
            [
                class_type
                for class_type in dao_module.__dict__.values()
                if isclass(class_type) and issubclass(class_type, BaseModel)
            ]
        )

    return connection
