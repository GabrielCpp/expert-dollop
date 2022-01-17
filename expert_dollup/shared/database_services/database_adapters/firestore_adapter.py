from typing import List, TypeVar, Optional, Dict, Type, Tuple, Union
from dataclasses import dataclass
from google.cloud.firestore import AsyncClient
from google.cloud.firestore_v1 import Increment
from google.auth.credentials import AnonymousCredentials
from expert_dollup.shared.automapping import Mapper
from ..query_filter import QueryFilter
from ..exceptions import RecordNotFound
from ..batch_helper import batch
from ..collection_mapper import CollectionMapper
from ..db_agnotist_query_builder import DbAgnotistQueryBuilder
from ..adapter_interfaces import (
    CollectionService,
    QueryBuilder,
    WhereFilter,
    DbConnection,
)


@dataclass
class FirestoreCollection:
    name: str
    pimary_keys: List[str]
    collection_count: bool
    key_counts: Dict[str, List[str]]


class FirestoreConnection(DbConnection):
    def __init__(self, connection_string: str, **kwargs):
        self.connection_string = connection_string
        self._client = AsyncClient(
            project="my-project", credentials=AnonymousCredentials()
        )
        self.collections: Dict[Type, FirestoreCollection] = {}

    def get_collection_service(self, meta: Type, mapper: Mapper):
        return FirestoreTableService(meta, self.collections, self._client, mapper)

    def load_metadatas(self, dao_types):
        self.collections = {}

        for dao_type in dao_types:
            if not hasattr(dao_type, "Meta"):
                continue

            schema = dao_type.schema()
            assert schema.get("type") == "object"
            assert "properties" in schema

            meta = dao_type.Meta
            table_name = schema["title"]
            pimary_keys = list(meta.pk) if isinstance(meta.pk, tuple) else [meta.pk]
            self.collections[dao_type] = FirestoreCollection(
                name=table_name,
                pimary_keys=pimary_keys,
                collection_count=True,
                key_counts={},
            )

    async def truncate_db(self, names: Optional[List[str]] = None):
        if names is None:
            names = [collection.name for collection in self.collections.values()]

        for name in names:
            async for doc in self._client.collection(name).stream():
                await doc.reference.delete()

    async def drop_db(self):
        await self.truncate_db()

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    @property
    def is_connected(self) -> bool:
        return True


SUPPORTED_OPS = {
    "==": lambda lhs, rhs: lhs == rhs,
    "in": lambda lhs, rhs: lhs.in_(rhs),
    "startwiths": lambda lhs, rhs: lhs.like(f"{rhs}%"),
}


class QueryCompiler:
    def compile_query(self, builder: DbAgnotistQueryBuilder, collection):
        query = collection

        for name in builder._selections:
            pass

        for (column_name, op, value) in builder._wheres:
            apply_op = SUPPORTED_OPS[op]
            query = apply_op(column_name, value, query)

        if not builder._orders is None:
            pass

        if not builder._max_records is None:
            query = query.limit(builder._max_records)

        return query


Domain = TypeVar("Domain")
Id = TypeVar("Id")
BATCH_SIZE = 500


class FirestoreTableService(CollectionService[Domain]):
    def __init__(
        self,
        meta: Type,
        tables_details: Dict[Type, FirestoreCollection],
        client: AsyncClient,
        mapper: Mapper,
    ):
        self.dao = meta.dao
        self.domain = meta.domain
        self._mapper = mapper
        self._client = client
        self._table_details = tables_details.get(meta.dao)
        self._collection = client.collection(self._table_details.name)
        self._dao_mapper = CollectionMapper(
            mapper,
            meta.domain,
            meta.dao,
            getattr(meta.dao.Meta, "version", None),
            getattr(meta.dao.Meta, "version_mappers", {}),
        )

    async def insert(self, domain: Domain):
        d = self._dao_mapper.map_to_dict(domain)
        id = self._get_document_id(d)
        await self._collection.document(id).set(d)

    async def insert_many(self, domains: List[Domain]):
        dicts = self._dao_mapper.map_many_to_dict(domains)
        for dicts_batch in batch(dicts, BATCH_SIZE):
            b = self._client.batch()

            for d in dicts_batch:
                id = self._get_document_id(d)
                b.set(id, d)

            b.commit()

    async def update(self, value_filter: QueryFilter, query_filter: WhereFilter):
        value_dict = self._mapper.map(value_filter, dict, value_filter.__class__)
        query = self._build_query(query_filter).limit(BATCH_SIZE)
        total_count = 0
        count = 0
        act = True

        while act:
            async for doc in query.stream():
                doc.update(value_dict)
                count += 1

            total_count += count

            if count >= BATCH_SIZE:
                count = 0
            else:
                act = False

        return total_count

    async def upserts(self, domains: List[Domain]) -> None:
        dicts = self._dao_mapper.map_many_to_dict(domains)
        for dicts_batch in batch(dicts, BATCH_SIZE):
            b = self._client.batch()

            for d in dicts_batch:
                b.set(d, {"merge": True})

            b.commit()

    async def find_all(self, limit: int = 1000) -> List[Domain]:
        results = []

        async for doc in self._collection.limit(limit).stream():
            results.append(doc)

        domains = self._dao_mapper.map_many_to_domain(results)
        return domains

    async def find_by(self, query_filter: WhereFilter) -> List[Domain]:
        results = []
        query = self._build_query(query_filter)

        async for doc in query.stream():
            results.append(doc)

        domains = self._dao_mapper.map_many_to_domain(results)
        return domains

    async def find_one_by(self, query_filter: WhereFilter) -> Domain:
        query = self._build_query(query_filter).limit(1)

        async for doc in query.stream():
            return self._dao_mapper.map_to_domain(doc)

        raise RecordNotFound()

    async def find_by_id(self, pk_id: Id) -> Domain:
        doc = self._collection.document(self._build_id(pk_id)).get()

        if doc is None:
            raise RecordNotFound()

        return self._dao_mapper.map_to_domain(doc)

    async def has(self, pk_id: Id) -> bool:
        doc = await self._collection.document(self._build_id(pk_id)).get()
        return not doc is None

    async def count(self, query_filter: Optional[WhereFilter] = None) -> int:
        pass

    async def delete_by(self, query_filter: WhereFilter):
        query = self._build_query(query_filter).limit(BATCH_SIZE)
        total_count = 0
        count = 0
        act = True

        while act:
            async for doc in query.stream():
                await doc.reference.delete()
                count += 1

            total_count += count

            if count >= BATCH_SIZE:
                count = 0
            else:
                act = False

        return total_count

    async def delete_by_id(self, pk_id: Id):
        id = self._build_id(pk_id)
        await self._collection.document(id).delete()

    def get_builder(self) -> QueryBuilder:
        return DbAgnotistQueryBuilder()

    def _get_document_id(self, d):
        pass

    def _build_query(self, builder: WhereFilter):
        if isinstance(builder, DbAgnotistQueryBuilder):
            return QueryCompiler.compile_query(builder, self._collection)

        return self._build_filter(builder)
