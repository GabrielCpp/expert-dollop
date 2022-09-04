from pymongo import UpdateOne
from bson.decimal128 import Decimal128
from decimal import Decimal
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
from pydantic import BaseModel
from typing import Callable, List, TypeVar, Optional, Dict, Type, Set, Any, Awaitable
from dataclasses import dataclass
from urllib.parse import urlparse
from expert_dollup.shared.automapping import Mapper
from ..query_filter import QueryFilter
from ..exceptions import RecordNotFound
from ..batch_helper import batch
from ..collection_element_mapping import CollectionElementMapping
from ..db_agnotist_query_builder import DbAgnotistQueryBuilder
from ..adapter_interfaces import (
    InternalRepository,
    QueryBuilder,
    WhereFilter,
    DbConnection,
    RepositoryMetadata,
)
from ..simplifier import Simplifier


def build_count_key_id(d, keys: Set[str]):
    return "count_" + "_".join(str(d[name]) for name in sorted(keys))


@dataclass
class CollectionDetails:
    name: str
    pimary_keys: List[str]
    collection_count: bool
    key_counts: Set[Set[str]]

    @property
    def is_counting_enabled(self) -> bool:
        return self.collection_count is True or len(self.key_counts) > 0

    def build_id(self, d):
        if len(self.pimary_keys) == 1:
            name = self.pimary_keys[0]
            return str(d[name])

        if len(self.pimary_keys) > 1:
            return "_".join(str(d[name]) for name in self.pimary_keys)

        assert False

    def build_id_from_pk(self, mapper, pk):
        if len(self.pimary_keys) == 1:
            return str(pk)

        if len(self.pimary_keys) > 1:
            d = self.unfold_query(pk, mapper)
            return "_".join(str(d[name]) for name in self.pimary_keys)

        return pk

    def build_counter_id(
        self, query_filter: Optional[WhereFilter], mapper: Mapper
    ) -> str:
        if query_filter is None:
            assert (
                self.collection_count is True
            ), f"Collection count is not enabled for this {self.name}"
            return COLLECTION_STATS_ID

        d = self.unfold_query(query_filter, mapper)
        keys_set = frozenset(d.keys())
        assert (
            keys_set in self.key_counts
        ), f"Filter type '{keys_set}' is unsuported by {self.name}, avaiable options are {self.key_counts}"

        return build_count_key_id(d, keys_set)

    def unfold_query(self, query_filter: QueryFilter, mapper: Mapper):
        d = mapper.map(query_filter, dict, query_filter.__class__)
        return d


from pymongo.errors import InvalidURI
from logging import getLogger

logger = getLogger("mongo")


class MongoConnection(DbConnection):
    def __init__(self, connection_string: str, **kwargs):
        try:
            self._client = AsyncIOMotorClient(
                connection_string,
                tz_aware=True,
                connect=False,
                uuidRepresentation="standard",
            )
        except InvalidURI as e:
            logger.exception(
                "Invalid URI",
                extra=dict(
                    connection_string=connection_string, original_message=str(e)
                ),
            )
            raise

        self.db_name = urlparse(connection_string).path.strip("/ ")
        self.collections: Dict[Type, CollectionDetails] = {}

    def get_collection_service(self, meta: RepositoryMetadata, mapper: Mapper):
        return MongoCollection(
            meta, self, self._client.get_database(self.db_name), mapper
        )

    def load_metadatas(self, metadatas: List[RepositoryMetadata]):
        self.collections = {}

        for metadata in metadatas:
            schema = metadata.dao.schema()
            assert schema.get("type") == "object"
            assert "properties" in schema

            meta = metadata.dao.Meta
            table_name = schema["title"]
            pimary_keys = list(meta.pk) if isinstance(meta.pk, tuple) else [meta.pk]
            options = getattr(meta, "options", {}).get("firestore", {})
            self.collections[metadata.dao] = CollectionDetails(
                name=table_name,
                pimary_keys=pimary_keys,
                collection_count=options.get("collection_count", False),
                key_counts=options.get("key_counts", set()),
            )

    async def truncate_db(self, names: Optional[List[str]] = None):
        if names is None:
            names = [c.name for c in self.collections.values()]

        db = self._client.get_database(self.db_name)

        for name in names:
            collection = db.get_collection(name)
            await collection.delete_many({})

    async def transaction(self, callback: Callable[[], Awaitable]):
        async with await self._client.start_session() as s:
            async with s.start_transaction():
                await callback()

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    @property
    def is_connected(self) -> bool:
        return True


def startwiths_op(lhs, rhs):
    assert isinstance(rhs, str), "Startwiths only support string"
    assert (
        len(rhs) > 0
    ), "Startwiths argument must not be empty string, otherwise just remove it from query"

    rhs_upper = rhs[:-1] + chr(ord(rhs[-1]) + 1)

    return [{lhs: {"$gte": rhs}}, {lhs: {"$lt": rhs_upper}}]


DESCENDING = -1
ASCENDING = 1
BATCH_SIZE = 500
COLLECTION_STATS_ID = "--stats--"
SUPPORTED_OPS = {
    "<": lambda lhs, rhs: [{lhs: {"$lt": rhs}}],
    "==": lambda lhs, rhs: [{lhs: {"$eq": rhs}}],
    "in": lambda lhs, rhs: [{lhs: {"$in": rhs}}],
    "startwiths": startwiths_op,
    "contain_one": lambda lhs, rhs: [{lhs: rhs}],
}
SIMLIFIERS = {Decimal: lambda v: Decimal128(str(v)), set: lambda value: list(value)}


class QueryCompiler:
    def __init__(self, mapper: Mapper, collection: AsyncIOMotorCollection):
        self._mapper = mapper
        self._collection = collection
        self._simplifier = Simplifier(SIMLIFIERS)

    def find(self, builder: WhereFilter):
        if isinstance(builder, QueryBuilder):
            return self.compile_query(builder)

        return self._collection.find(self.build_filter(builder))

    def build_filter(self, builder: Optional[WhereFilter]) -> dict:
        if builder is None:
            return {}

        conditions = []

        if isinstance(builder, QueryBuilder):
            for (column_name, op, value) in builder._wheres:
                apply_op = SUPPORTED_OPS[op]
                simplified_value = self.simplify(value)
                condition = apply_op(column_name, simplified_value)
                conditions.extend(condition)
        else:
            column_value_dict = self._mapper.map(builder, dict)
            for (column_name, value) in column_value_dict.items():
                simplified_value = self.simplify(value)
                conditions.append({column_name: {"$eq": simplified_value}})

        if len(conditions) == 0:
            return {}

        if len(conditions) == 1:
            return conditions[0]

        return {"$and": conditions}

    def compile_query(self, builder: DbAgnotistQueryBuilder):
        selections = None
        query_filter = self.build_filter(builder)
        orders = {}

        if not builder._selections is None:
            selections = {}

            for selection in builder._selections:
                selections[selection] = 1

        if not builder._orders is None:
            for name, direction in builder._orders:
                orders[name] = DESCENDING if direction == "desc" else ASCENDING

        query = self._collection.find(
            query_filter
            if len(orders) == 0
            else {"$query": query_filter, "$orderby": orders},
            selections,
        )

        if not builder._max_records is None:
            query = query.limit(builder._max_records)

        return query

    def simplify(self, value):
        return self._simplifier.simplify(value)


Domain = TypeVar("Domain")
Id = TypeVar("Id")


class MongoCollection(InternalRepository[Domain]):
    def __init__(
        self,
        meta: RepositoryMetadata,
        parent: MongoConnection,
        client: AsyncIOMotorDatabase,
        mapper: Mapper,
    ):
        self._parent = parent
        self._domain = meta.domain
        self._mapper = mapper
        self._client = client
        self._table_details = parent.collections[meta.dao]
        self._collection = client.get_collection(self._table_details.name)
        self._query_compiler = QueryCompiler(mapper, self._collection)
        self._db_mapping = CollectionElementMapping(
            mapper,
            meta.domain,
            meta.dao,
            getattr(meta.dao.Meta, "version", None),
            getattr(meta.dao.Meta, "version_mappers", {}),
            getattr(meta.dao.Meta, "type_of", None),
            dao_to_dict=self._dao_to_dict,
        )

    @property
    def domain(self) -> Type:
        return self._domain

    @property
    def batch_size(self) -> int:
        return 1000

    @property
    def db(self) -> DbConnection:
        return self._parent

    async def insert(self, domain: Domain):
        document = self._db_mapping.map_to_dict(domain)
        await self._collection.insert_one(document)

    async def insert_many(self, domains: List[Domain]):
        dicts = self._db_mapping.map_many_to_dict(domains)
        for dicts_batch in batch(dicts, BATCH_SIZE):
            await self._collection.insert_many(dicts_batch)

    async def update(self, value_filter: QueryFilter, where_filter: WhereFilter):
        value_dict = self._table_details.unfold_query(value_filter, self._mapper)
        simplified_dict = self._query_compiler.simplify(value_dict)
        compiled_filter = self._query_compiler.build_filter(where_filter)
        await self._collection.update_many(compiled_filter, {"$set": simplified_dict})

    async def upserts(self, domains: List[Domain]) -> None:
        dicts = self._db_mapping.map_many_to_dict(domains)

        for docs in batch(dicts, BATCH_SIZE):
            operations = [
                UpdateOne(
                    {"_id": doc["_id"]},
                    {"$set": doc},
                    upsert=True,
                )
                for doc in docs
            ]

            await self._collection.bulk_write(operations, ordered=False)

    async def find_all(self, limit: int = 1000) -> List[Domain]:
        results = []

        async for doc in self._collection.find().limit(limit):
            results.append(doc)

        domains = self._db_mapping.map_many_to_domain(results)
        return domains

    async def find_by(self, query_filter: WhereFilter) -> List[Domain]:
        query = self._query_compiler.find(query_filter)
        results = await query.to_list(length=None)
        domains = self._db_mapping.map_many_to_domain(results)
        return domains

    async def find_one_by(self, query_filter: WhereFilter) -> Domain:
        query = self._query_compiler.find(query_filter).limit(1)

        async for doc in query:
            return self._db_mapping.map_to_domain(doc)

        raise RecordNotFound()

    async def find_by_id(self, pk_id: Id) -> Domain:
        document_id = self._table_details.build_id_from_pk(self._mapper, pk_id)
        doc = await self._collection.find_one({"_id": document_id})

        if doc is None:
            raise RecordNotFound()

        return self._db_mapping.map_to_domain(doc)

    async def has(self, pk_id: Id) -> bool:
        document_id = self._table_details.build_id_from_pk(self._mapper, pk_id)
        doc = await self._collection.find_one({"_id": document_id})
        return not doc is None

    async def exists(self, query_filter: WhereFilter) -> bool:
        query = self._query_compiler.find(query_filter).limit(1)

        async for _ in query:
            return True

        return False

    async def count(self, query_filter: Optional[WhereFilter] = None) -> int:
        counter_filter = self._query_compiler.build_filter(query_filter)
        count = await self._collection.count_documents(counter_filter)
        return count

    async def delete_by(self, query_filter: WhereFilter):
        compiled_filter = self._query_compiler.build_filter(query_filter)
        await self._collection.delete_many(compiled_filter)

    async def delete_by_id(self, pk_id: Id):
        document_id = self._table_details.build_id_from_pk(self._mapper, pk_id)
        await self._collection.delete_many({"_id": document_id})

    # Extended api

    def get_builder(self) -> QueryBuilder:
        return DbAgnotistQueryBuilder()

    async def fetch_all_records(
        self,
        builder: WhereFilter,
        mappings: Dict[str, Callable[[Mapper], Callable[[Any], Any]]] = {},
    ) -> List[dict]:
        query = self._query_compiler.find(builder)
        results = []
        value_mapper = {
            name: mapping(self._mapper) for name, mapping in mappings.items()
        }

        async for doc in query:
            results.append(
                {
                    name: value_mapper[name](value) if name in value_mapper else value
                    for name, value in doc.items()
                }
            )

        return results

    async def bulk_insert(self, daos: List[BaseModel]) -> None:
        dicts = self._db_mapping.map_many_dao_to_dict(daos)

        for dicts_batch in batch(dicts, BATCH_SIZE):
            await self._collection.insert_many(dicts_batch)

    def map_domain_to_dao(self, domain: Domain) -> BaseModel:
        return self._db_mapping.map_domain_to_dao(domain)

    def unpack_query(self, query_filter: QueryFilter) -> dict:
        return self._table_details.unfold_query(query_filter, self._mapper)

    def _dao_to_dict(self, model: BaseModel) -> dict:
        document = self._query_compiler.simplify(model)
        document["_id"] = self._table_details.build_id(document)
        return document
