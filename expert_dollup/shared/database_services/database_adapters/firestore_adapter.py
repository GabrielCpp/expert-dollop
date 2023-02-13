from typing import Callable, Iterable, List, TypeVar, Optional, Dict, Type, Set, Any
from dataclasses import dataclass
from collections import defaultdict
from os import environ
from pydantic import BaseModel
from google.cloud.firestore import (
    AsyncClient,
    AsyncWriteBatch,
    AsyncCollectionReference,
    Query,
)
from google.cloud.firestore_v1 import Increment
from google.api_core.retry import Retry, if_exception_type
from google.auth.credentials import AnonymousCredentials
from expert_dollup.shared.automapping import Mapper
from ..query_filter import QueryFilter
from ..exceptions import RecordNotFound
from ..batch_helper import batch
from ..collection_element_mapping import CollectionElementMapping
from ..simplifier import Simplifier
from ..adapter_interfaces import (
    InternalRepository,
    QueryBuilder,
    WhereFilter,
    DbConnection,
    RepositoryMetadata,
)

import google.cloud.exceptions as exceptions
import google.api_core.exceptions as core_exceptions
import google.auth.exceptions as auth_exceptions
import requests.exceptions

if_extended_transient_error = if_exception_type(
    exceptions.InternalServerError,
    exceptions.TooManyRequests,
    exceptions.ServiceUnavailable,
    requests.exceptions.ConnectionError,
    requests.exceptions.ChunkedEncodingError,
    auth_exceptions.TransportError,
    core_exceptions.Cancelled,
)

retry_strategy = Retry(if_extended_transient_error)


@dataclass
class CollectionDetails:
    name: str
    pimary_keys: List[str]
    collection_count: bool
    key_counts: Set[Set[str]]

    @property
    def is_counting_enabled(self) -> bool:
        return self.collection_count is True or len(self.key_counts) > 0


class FirestoreConnection(DbConnection):
    def __init__(self, connection_string: str, **kwargs):
        self.connection_string = connection_string

        options = {}

        if "FIRESTORE_EMULATOR_HOST" in environ:
            options["project"] = "my-project"
            options["credentials"] = AnonymousCredentials()

        self._client = AsyncClient(**options)
        self.collections: Dict[Type, CollectionDetails] = {}

    def get_collection_service(self, meta: RepositoryMetadata, mapper: Mapper):
        return FirestoreCollection(meta, self.collections, self._client, mapper)

    def load_metadatas(self, metadatas: List[RepositoryMetadata]):
        def get_dao(dao):
            for t in get_args(dao):
                return t.schema(), t.Meta
            else:
                return dao.schema(), dao.Meta

        self.collections = {}

        for metadata in metadatas:
            schema, meta = get_dao(metadata.dao)
            assert schema.get("type") == "object"
            assert "properties" in schema

            table_name = schema["title"]
            pimary_keys = list(meta.pk) if isinstance(meta.pk, tuple) else [meta.pk]
            options = getattr(meta, "options", {}).get("firestore", {})
            self.collections[metadata.dao] = CollectionDetails(
                name=table_name,
                pimary_keys=pimary_keys,
                collection_count=options.get("collection_count", False),
                key_counts=options.get("key_counts", set()),
            )

    async def truncate_db(self):
        for collection in self.collections.values():
            async for doc in self._client.collection(collection.name).stream():
                await doc.reference.delete()

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    @property
    def is_connected(self) -> bool:
        return True


def startwiths_op(lhs, rhs, query):
    assert isinstance(rhs, str), "Startwiths only support string"
    assert (
        len(rhs) > 0
    ), "Startwiths argument must not be empty string, otherwise just remove it from query"

    return query.where(lhs, ">=", rhs).where(lhs, "<", rhs[:-1] + chr(ord(rhs[-1]) + 1))


BATCH_SIZE = 500
COLLECTION_STATS_ID = "--stats--"
SUPPORTED_OPS = {
    "<": lambda lhs, rhs, query: query.where(lhs, "<", rhs),
    "==": lambda lhs, rhs, query: query.where(lhs, "==", rhs),
    "in": lambda lhs, rhs, query: query.where(lhs, "in", rhs),
    "startwiths": startwiths_op,
}


class QueryCompiler:
    def __init__(self, collection: AsyncCollectionReference):
        self.collection = collection

    def compile_query(self, builder: QueryBuilder):
        query = self.collection

        if not builder.selections is None:
            has_one_item = len(builder.selections) == 1

            if has_one_item and builder.selections[0] == "1":
                query = query.select(["__name__"])
            elif has_one_item and builder.selections[0] == "*":
                pass
            else:
                query = query.select(builder.selections)

        for (column_name, op, value) in builder.wheres:
            apply_op = SUPPORTED_OPS[op]
            query = apply_op(column_name, Simplifier.simplify(value), query)

        if not builder.orders is None:
            for name, direction in builder.orders:
                query = query.order_by(
                    name,
                    direction=Query.DESCENDING
                    if direction == "desc"
                    else Query.ASCENDING,
                )

        if not builder.limit_value is None:
            query = query.limit(builder.limit_value)

        return query

    def build_count_key_id(self, d, keys: Set[str]):
        return "count_" + "_".join(str(d[name]) for name in sorted(keys))


class BatchProxy:
    def __init__(
        self,
        make_batch: Callable[[], AsyncWriteBatch],
        collection_details: CollectionDetails,
        query_compiler: QueryCompiler,
    ) -> None:
        self._make_batch = make_batch
        self._batch = make_batch()
        self.collection_count = 0
        self.keys_count = defaultdict(int)
        self._query_compiler = query_compiler
        self._collection_details = collection_details

    def set(self, doc_ref, d):
        self.collection_count += 1
        for keys in self._collection_details.key_counts:
            count_id = self._query_compiler.build_count_key_id(d, keys)
            self.keys_count[count_id] += 1

        self._batch.set(doc_ref, d)

    def delete(self, doc_ref, d):
        self.collection_count -= 1
        for keys in self._collection_details.key_counts:
            count_id = self._query_compiler.build_count_key_id(d, keys)
            self.keys_count[count_id] -= 1

        self._batch.delete(doc_ref)

    def update(self, doc_ref, d):
        self._batch.update(doc_ref, d)

    @property
    def count_related_updates(self) -> int:
        count = 1 if self._collection_details.collection_count else 0
        count += len(self.keys_count)
        return count

    @property
    def is_batch_full(self) -> bool:
        return self.collection_count + self.count_related_updates == BATCH_SIZE

    async def commit(self):
        self._add_counter_updates()
        await self._batch.commit(retry_strategy)
        self._batch = self._make_batch()
        self.collection_count = 0
        self.keys_count = defaultdict(int)

    def _add_counter_updates(self):
        if self._collection_details.collection_count and self.collection_count != 0:
            doc_ref = self._query_compiler.collection.document(COLLECTION_STATS_ID)
            self._batch.set(
                doc_ref, {"count": Increment(self.collection_count)}, merge=True
            )

        for doc_id, increment in self.keys_count.items():
            if increment == 0:
                continue

            doc_ref = self._query_compiler.collection.document(doc_id)
            self._batch.set(doc_ref, {"count": Increment(increment)}, merge=True)


Domain = TypeVar("Domain")
Id = TypeVar("Id")


def record_to_dict(r) -> dict:
    return r.to_dict()


class FirestoreCollection(InternalRepository[Domain]):
    def __init__(
        self,
        meta: RepositoryMetadata,
        tables_details: Dict[Type, CollectionDetails],
        client: AsyncClient,
        mapper: Mapper,
    ):
        self._domain = meta.domain
        self._mapper = mapper
        self._client = client
        self._table_details = tables_details.get(meta.dao)
        self._collection = client.collection(self._table_details.name)
        self._query_compiler = QueryCompiler(self._collection)
        self._db_mapping = CollectionElementMapping(
            mapper,
            CollectionElementMapping.get_mapping_details(meta.domain, meta.dao),
            Simplifier.simplify,
            record_to_dict=record_to_dict,
        )

    @property
    def domain(self) -> Type:
        return self._domain

    @property
    def batch_size(self) -> int:
        return 20

    async def insert(self, domain: Domain):
        d = self._db_mapping.map_domain_to_dict(domain)

        if self._table_details.is_counting_enabled:
            await self._batch_operation([d], lambda b, doc_ref, d: b.set(doc_ref, d))
        else:
            doc_id = self._build_id(d)
            await self._collection.document(doc_id).set(d, retry=retry_strategy)

    async def insert_many(self, domains: List[Domain]):
        dicts = self._db_mapping.map_many_domain_to_dict(domains)
        await self._batch_operation(dicts, lambda b, doc_ref, d: b.set(doc_ref, d))

    async def update(self, value_filter: QueryFilter, query_filter: WhereFilter):
        value_dict = self._mapper.map(value_filter, dict, value_filter.__class__)
        value_dict = Simplifier.simplify(value_dict)

        return await self._streamed_batch_operation(
            query_filter, lambda b, doc_ref, d: b.update(doc_ref, value_dict)
        )

    async def upserts(self, domains: List[Domain]) -> None:
        dicts = self._db_mapping.map_many_domain_to_dict(domains)
        await self._batch_operation(
            dicts, lambda b, doc_ref, d: b.set(doc_ref, d, merge=True)
        )

    async def find_all(self, limit: int = 1000) -> List[Domain]:
        results = []

        async for doc in self._collection.limit(limit).stream():
            results.append(doc)

        domains = self._db_mapping.map_many_record_to_domain(results)
        return domains

    async def find_by(self, query_filter: WhereFilter) -> List[Domain]:
        results = []
        query = self._build_query(query_filter)

        async for doc in query.stream():
            results.append(doc)

        domains = self._db_mapping.map_many_record_to_domain(results)
        return domains

    async def find_one_by(self, query_filter: WhereFilter) -> Domain:
        query = self._build_query(query_filter).limit(1)

        async for doc in query.stream():
            return self._db_mapping.map_record_to_domain(doc)

        raise RecordNotFound()

    async def find_by_id(self, pk_id: Id) -> Domain:
        document_id = self._build_id_from_pk(pk_id)
        doc = await self._collection.document(document_id).get()

        if doc.exists:
            return self._db_mapping.map_record_to_domain(doc)

        raise RecordNotFound()

    async def has(self, pk_id: Id) -> bool:
        document_id = self._build_id_from_pk(pk_id)
        doc = await self._collection.document(document_id).get()
        return doc.exists

    async def exists(self, query_filter: WhereFilter) -> bool:
        query = self._build_query(query_filter).limit(1)

        async for doc in query.stream():
            return True

        return False

    async def count(self, query_filter: Optional[WhereFilter] = None) -> int:
        counter_id = self._build_counter_id(query_filter)
        doc = await self._collection.document(counter_id).get()

        if doc.exists:
            return int(doc.to_dict().get("count"))

        return 0

    async def delete_by(self, query_filter: WhereFilter):
        return await self._streamed_batch_operation(
            query_filter, lambda b, doc_ref, d: b.delete(doc_ref, d)
        )

    async def delete_by_id(self, pk_id: Id):
        id = self._build_id_from_pk(pk_id)
        await self._collection.document(id).delete()

    async def execute(self, builder: QueryBuilder) -> Union[Domain, List[Domain], None]:
        pass

    async def build_query(self, query_filter: QueryFilter) -> QueryBuilder:
        return self._build_query(query_filter)

    async def fetch_all_records(
        self,
        builder: WhereFilter,
        mappings: Dict[str, Callable[[Mapper], Callable[[Any], Any]]] = {},
    ) -> List[dict]:
        query = self._build_query(builder)
        results = []
        value_mapper = {
            name: mapping(self._mapper) for name, mapping in mappings.items()
        }

        async for doc in query.stream():
            d = {
                name: value_mapper[name](value) if name in value_mapper else value
                for name, value in record_to_dict(doc).items()
            }

            results.append(d)

        return results

    async def bulk_insert(self, daos: List[BaseModel]):
        dicts = self._db_mapping.map_many_dao_to_dict(daos)
        await self._batch_operation(dicts, lambda b, doc_ref, d: b.set(doc_ref, d))

    def map_domain_to_dao(self, domain: Domain) -> BaseModel:
        return self._db_mapping.map_domain_to_dao(domain)

    async def _batch_operation(self, dicts: Iterable[dict], act: callable):
        for dicts_batch in batch(dicts, BATCH_SIZE):
            b = BatchProxy(
                self._client.batch, self._table_details, self._query_compiler
            )

            for d in dicts_batch:
                doc_id = self._build_id(d)
                doc_ref = self._collection.document(doc_id)
                act(b, doc_ref, d)

                if b.is_batch_full:
                    await b.commit()

            await b.commit()

    async def _streamed_batch_operation(self, query_filter: WhereFilter, act: callable):
        query = self._build_query(query_filter).limit(BATCH_SIZE)
        total_count = 0
        count = 0
        in_progress = True
        b = BatchProxy(self._client.batch, self._table_details, self._query_compiler)

        while in_progress:
            async for doc in query.stream():
                act(b, doc.reference, doc)
                count += 1

                if b.is_batch_full:
                    await b.commit()

            await b.commit()

            total_count += count

            if count >= BATCH_SIZE:
                count = 0
            else:
                in_progress = False

        return total_count

    def _build_id(self, d):
        if len(self._table_details.pimary_keys) == 1:
            name = self._table_details.pimary_keys[0]
            return str(d[name])

        if len(self._table_details.pimary_keys) > 1:
            return "_".join(str(d[name]) for name in self._table_details.pimary_keys)

        assert False

    def _build_id_from_pk(self, pk):
        if len(self._table_details.pimary_keys) == 1:
            return str(pk)

        if len(self._table_details.pimary_keys) > 1:
            d = self._mapper.map(pk, dict, pk.__class__)
            return "_".join(str(d[name]) for name in self._table_details.pimary_keys)

        return pk

    def _build_counter_id(self, query_filter: Optional[WhereFilter]) -> str:
        if query_filter is None:
            assert (
                self._table_details.collection_count is True
            ), f"Collection count is not enabled for this {self._table_details.name}"
            return COLLECTION_STATS_ID

        d = self._mapper.map(query_filter, dict, query_filter.__class__)
        keys_set = frozenset(d.keys())
        assert (
            keys_set in self._table_details.key_counts
        ), f"Filter type '{keys_set}' is unsuported by {self._table_details.name}, avaiable options are {self._table_details.key_counts}"

        return self._query_compiler.build_count_key_id(d, keys_set)

    def _build_query(self, builder: WhereFilter):
        if isinstance(builder, QueryBuilder):
            return self._query_compiler.compile_query(builder)

        query = self._query_compiler.collection
        column_value_dict = self._mapper.map(builder, dict)
        for (column_name, value) in column_value_dict.items():
            simplified_value = Simplifier.simplify(value)
            query = query.where(column_name, "==", simplified_value)

        return query
