from dataclasses import dataclass
from typing import Callable
from ..query_filter import QueryFilter
from ..exceptions import RecordNotFound
from ..collection_element_mapping import CollectionElementMapping
from ..adapter_interfaces import (
    InternalRepository,
    QueryBuilder,
    WhereFilter,
    DbConnection,
    RepositoryMetadata,
)
from ..storage_connectors import StorageClient


@dataclass
class CollectionDetails:
    encode: Callable[[dict], bytes]
    decode: Callable[[bytes], dict]
    key_of: Callable[[dict], str]


class BucketConnection(DbConnection):
    def __init__(self, connection_string: str, **kwargs):
        schema, bucket = connection_string.split("://", 2)

        if schema == "file":
            from ..storage_connectors import LocalStorage

            self._client = LocalStorage(bucket)
        elif schema == "gcs":
            from ..storage_connectors import GoogleCloudStorage

            self._client = GoogleCloudStorage(bucket)
        else:
            raise Exception(f"Unrecognized schema {schema}")

        self.collections: Dict[Type, CollectionDetails] = {}

    def get_collection_service(self, meta: RepositoryMetadata, mapper: Mapper):
        return BucketCollection(meta, self, self._client, mapper)

    def load_metadatas(self, metadatas: List[RepositoryMetadata]):
        def get_dao(dao):
            for t in get_args(dao):
                return t.schema(), t.Meta
            else:
                return dao.schema(), dao.Meta

        self.collections = {}

        for metadata in metadatas:
            _, meta = get_dao(metadata.dao)
            self.collections[metadata.dao] = CollectionDetails(
                meta.encode, meta.decode, meta.key_of
            )

    async def truncate_db(self):
        next_page_token = None
        page = await self._client.list_by_page(prefix, next_page_token)

        while len(page.results) >= total_count:
            next_page_token = page.next_page_token

            for result in page.results:
                self._client.delete(result.key)

    async def transaction(self, callback: Callable[[], Awaitable]):
        await callback()

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    @property
    def is_connected(self) -> bool:
        return True


class BucketCollection(InternalRepository[Domain]):
    def __init__(
        self,
        meta: RepositoryMetadata,
        parent: BucketConnection,
        client: StorageClient,
        mapper: Mapper,
    ):
        self._parent = parent
        self._domain = meta.domain
        self._client = client
        self._mapper = mapper
        self._object = parent.collections[meta.dao]
        self._db_mapping = CollectionElementMapping(
            mapper, CollectionElementMapping.get_mapping_details(meta.domain, meta.dao)
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
        document = self._db_mapping.map_domain_to_dict(domain)
        await self._write(document)

    async def inserts(self, domains: List[Domain]):
        documents = self._db_mapping.map_many_domain_to_dict(domains)
        await self._writes(documents)

    async def update(self, value_filter: QueryFilter, where_filter: WhereFilter):
        document_patch = self._db_mapping.map_domain_to_dict(domain)
        prefix = self._mapper.map(where_filter, str)

        async for result in self._stream(where_filter):
            original_document = await self._read(result.key)

            if original_document is None:
                continue

            document = {**original_document, **document_patch}

            if self._object.key_of(document) != result.key:
                await self._client.delete(result.key)

            await self._write(document)

    async def upserts(self, domains: List[Domain]) -> None:
        documents = self._db_mapping.map_many_domain_to_dict(domains)
        await self._writes(documents)

    async def all(self, limit: int = 1000) -> List[Domain]:
        results = await self._list("", limit)
        domains = self._db_mapping.map_many_record_to_domain(results)
        return domains

    async def find_by(self, query_filter: WhereFilter) -> List[Domain]:
        prefix = self._mapper.map(where_filter, str)
        results = await self._list(prefix, self.batch_size)
        domains = self._db_mapping.map_many_record_to_domain(results)
        return domains

    async def find_one_by(self, query_filter: WhereFilter) -> Domain:
        prefix = self._mapper.map(where_filter, str)

        async for doc in self._stream(prefix):
            return self._db_mapping.map_record_to_domain(doc)

        raise RecordNotFound()

    async def find(self, pk_id: Id) -> Domain:
        doc = await self._read(pk_id)

        if doc is None:
            raise RecordNotFound()

        return self._db_mapping.map_record_to_domain(doc)

    async def has(self, pk_id: Id) -> bool:
        return await self._client.exists(pk_id)

    async def exists(self, query_filter: WhereFilter) -> bool:
        prefix = self._mapper.map(where_filter, str)

        async for _ in self._stream(prefix):
            return True

        return False

    async def count(self, query_filter: Optional[WhereFilter] = None) -> int:
        prefix = "" if query_filter is None else self._mapper.map(query_filter, str)
        page = await self._client.list_by_page(prefix)
        return page.total_count

    async def delete_by(self, query_filter: WhereFilter):
        prefix = self._mapper.map(where_filter, str)

        async for result in self._stream(prefix):
            await self._client.delete(result.key)

    async def delete(self, pk_id: Id):
        await self._client.delete(pk_id)

    # Extended api

    async def fetch_all_records(
        self,
        builder: WhereFilter,
        mappings: Dict[str, Callable[[Mapper], Callable[[Any], Any]]] = {},
    ) -> List[dict]:
        results = []
        prefix = self._mapper.map(builder, str)
        value_mapper = {
            name: mapping(self._mapper) for name, mapping in mappings.items()
        }

        async for doc in self._stream(prefix):
            results.append(
                {
                    name: value_mapper[name](value) if name in value_mapper else value
                    for name, value in doc.items()
                }
            )

        return results

    async def bulk_insert(self, daos: List[BaseModel]) -> None:
        documents = self._db_mapping.map_many_dao_to_dict(daos)
        await self._writes(documents)

    def map_domain_to_dao(self, domain: Domain) -> BaseModel:
        return self._db_mapping.map_domain_to_dao(domain)

    async def execute(self, builder: WhereFilter) -> Optional[Domain]:
        raise NotImplementedError()

    async def _write(self, document: dict):
        key = self._object.key_of(document)
        data = self._object.encode(document)
        await self._client.upload_binary(key, data)

    async def _writes(self, documents: List[dict]):
        for document in documents:
            await self._write(document)

    async def _read(self, key: str) -> Optional[dict]:
        data = self._client.download_binary(key)

        if data is None:
            return None

        return self._object.decode(data)

    async def _stream(self, prefix: str):
        next_page_token = None
        page = await self._client.list_by_page(prefix, next_page_token)

        while len(page.results) >= total_count:
            next_page_token = page.next_page_token

            for result in page.results:
                yield result

            page = await self._client.list_by_page(prefix, next_page_token)

        for result in page.results:
            yield result

    async def _list(self, prefix: str, limit: int) -> List[dict]:
        results = []

        async for document in self._stream(prefix):
            if len(results) >= limit:
                break

            results.append(document)

        return results
