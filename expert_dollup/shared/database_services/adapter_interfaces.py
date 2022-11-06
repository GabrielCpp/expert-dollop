from abc import ABC, abstractmethod
from typing import (
    Generic,
    TypeVar,
    List,
    Optional,
    Union,
    Type,
    Dict,
    Any,
    Callable,
    Awaitable,
)
from typing_extensions import TypeAlias
from dataclasses import dataclass
from pydantic import BaseModel
from urllib.parse import urlparse
from expert_dollup.shared.automapping import Mapper
from .page import Page
from .query_filter import QueryFilter


class QueryBuilder(ABC):
    @abstractmethod
    def select(self, *names: str) -> "QueryBuilder":
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
WhereFilter: TypeAlias = Union[QueryFilter, QueryBuilder]


class Repository(ABC, Generic[Domain]):
    @property
    @abstractmethod
    def domain(self) -> Type:
        pass

    @property
    @abstractmethod
    def batch_size(self) -> int:
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
    async def exists(self, query_filter: WhereFilter) -> bool:
        pass

    @abstractmethod
    async def count(self, query_filter: Optional[WhereFilter] = None) -> int:
        pass


class InternalRepository(Repository[Domain]):
    @abstractmethod
    def get_builder(self) -> QueryBuilder:
        pass

    @abstractmethod
    async def fetch_all_records(
        self,
        builder: QueryBuilder,
        mappings: Dict[str, Callable[[Mapper], Callable[[Any], Any]]] = {},
    ) -> dict:
        pass

    @abstractmethod
    async def bulk_insert(self, daos: List[BaseModel]) -> None:
        pass

    @abstractmethod
    def map_domain_to_dao(self, domain: Domain) -> BaseModel:
        pass

    @abstractmethod
    def unpack_query(self, query: QueryFilter) -> dict:
        pass

    @abstractmethod
    async def apply_construct(self, builder: QueryBuilder) -> Optional[Domain]:
        pass


@dataclass
class RepositoryMetadata:
    domain: Type
    dao: Type


class DbConnection(ABC):
    _REGISTRY = {}

    @abstractmethod
    def load_metadatas(self, metadatas: List[RepositoryMetadata]) -> None:
        pass

    @abstractmethod
    def get_collection_service(
        self, meta: RepositoryMetadata, mapper: Mapper
    ) -> InternalRepository[Domain]:
        pass

    @abstractmethod
    async def truncate_db(self) -> None:
        pass

    @abstractmethod
    async def transaction(self, callback: Callable[[], Awaitable]) -> None:
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


class TokenEncoder(ABC):
    @abstractmethod
    def extend_query(
        self, builder: WhereFilter, limit: int, next_page_token: Optional[str]
    ) -> QueryBuilder:
        pass

    @abstractmethod
    def encode(self, dao: BaseModel):
        pass

    @abstractmethod
    def encode_field(self, dao_id: str):
        pass

    @abstractmethod
    def decode(self, cursor: str) -> Any:
        pass


@dataclass
class PaginationDetails:
    default_page_encoder: TokenEncoder
    for_domain: Type


def create_connection(connection_string: str, **kwargs) -> DbConnection:
    scheme = urlparse(connection_string).scheme

    if len(DbConnection._REGISTRY) == 0:
        try:
            from .database_adapters.postgres_adapter import PostgresConnection

            DbConnection._REGISTRY["postgresql+asyncpg"] = PostgresConnection
        except:
            pass

        try:
            from .database_adapters.firestore_adapter import FirestoreConnection

            DbConnection._REGISTRY["firestore+async"] = FirestoreConnection
        except:
            pass

        try:
            from .database_adapters.mongo_adapter import MongoConnection

            DbConnection._REGISTRY["mongodb"] = MongoConnection
            DbConnection._REGISTRY["mongodb+srv"] = MongoConnection
        except:
            pass

    build_connection = DbConnection._REGISTRY.get(scheme)

    if build_connection is None:
        raise KeyError(f"No key for schema {scheme}")

    connection = build_connection(connection_string, **kwargs)

    return connection
