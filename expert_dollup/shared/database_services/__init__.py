from abc import ABC, abstractmethod
from typing import (
    List,
    TypeVar,
    Optional,
    Generic,
    Awaitable,
    AsyncGenerator,
    Any,
    Tuple,
    Dict,
    Union,
)
from pydantic import BaseModel
from sqlalchemy import and_, Table
from sqlalchemy.schema import FetchedValue
from sqlalchemy.sql import select
from databases import Database
from dataclasses import dataclass
from sqlalchemy.dialects import postgresql
from expert_dollup.shared.automapping import Mapper
from expert_dollup.core.exceptions import RessourceNotFound
from .page import Page


Domain = TypeVar("Domain")
Id = TypeVar("Id")
Query = TypeVar("Query")


class AbstractFilterBuilder(ABC):
    @abstractmethod
    def build(self, filter: Query):
        pass


class AndColumnFilter(AbstractFilterBuilder):
    def __init__(self, pairs):
        self.pairs = pairs

    def build(self, query_filter: Query):
        condition = self.pairs[0][0] == self.pairs[0][1](query_filter)

        for index in range(1, len(self.pairs)):
            (column, get_value) = self.pairs[index]
            condition = and_(condition, column == get_value(query_filter))

        return condition


def build_and_column_filter(table, fields: dict):
    condition = None

    for column_name, value in fields.items():
        if condition is None:
            condition = getattr(table.c, column_name) == value
        else:
            condition = and_(condition, getattr(table.c, column_name) == value)

    return condition


class QueryFilter(BaseModel):
    class Config:
        allow_mutation = False

    def __init__(self, **kwargs):
        BaseModel.__init__(self, **kwargs)
        self.__dict__["_args"] = kwargs

    @property
    def args(self) -> dict:
        return self._args


def map_dict_keys(
    args: dict, mapping: Dict[str, Tuple[str, Union[None, callable]]]
) -> dict:
    mapped_args = {}

    for (key, value) in args.items():
        if key in mapping:
            (mapped_key, map_value) = mapping[key]
            mapped_args[mapped_key] = value if map_value is None else map_value(value)
        else:
            mapped_args[mapped_key] = value

    return mapped_args


@dataclass
class TableColumnProcessor:
    name: str
    processor: callable


class CoreCrudTableService(ABC, Generic[Domain]):
    def __init__(self, database: Database, mapper: Mapper):
        self._database = database
        self._mapper = mapper
        self._table = self.__class__.Meta.table
        self._dao = self.__class__.Meta.dao
        self._domain = self.__class__.Meta.domain
        self._table_filter_type = self.__class__.Meta.table_filter_type
        self._seach_filters = self.__class__.Meta.seach_filters or {}
        self._column_processors = self.build_table_raw_processors()

    def build_table_raw_processors(self) -> List[TableColumnProcessor]:
        noop = lambda x: x
        dialect = postgresql.dialect()

        return [
            TableColumnProcessor(
                name=column.name, processor=column.type.bind_processor(dialect) or noop
            )
            for column in self._table.c
            if not isinstance(column.server_default, FetchedValue)
        ]

    async def insert(self, domain: Domain) -> Awaitable:
        query = self._table.insert()
        value = self._mapper.map(domain, self._dao).dict()
        await self._database.execute(query=query, values=value)

    async def insert_many(self, domains: List[Domain]) -> Awaitable:
        daos = self._mapper.map_many(domains, self._dao)
        await self.insert_many_raw(daos)

    async def find_all(self, limit: int = 1000) -> Awaitable[List[Domain]]:
        query = self._table.select().limit(limit)
        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)
        return results

    async def find_by(
        self,
        query_filter: QueryFilter,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Awaitable[List[Domain]]:
        assert not self._table_filter_type is None
        filter_fields = self._mapper.map(query_filter, dict, self._table_filter_type)
        where_filter = build_and_column_filter(self._table, filter_fields)
        query = self._table.select().where(where_filter)

        if not limit is None:
            query = query.limit(limit)

        if not offset is None:
            query = query.offset(offset)

        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)

        return results

    async def find_one_by(self, query_filter: QueryFilter) -> Awaitable[List[Domain]]:
        assert not self._table_filter_type is None
        filter_fields = self._mapper.map(query_filter, dict, self._table_filter_type)
        where_filter = build_and_column_filter(self._table, filter_fields)
        query = self._table.select().where(where_filter)
        record = await self._database.fetch_one(query=query)

        if record is None:
            raise RessourceNotFound()

        result = self._mapper.map(self._dao(**record), self._domain)

        return result

    async def query_by(
        self,
        query_filter: Query,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Awaitable[List[Domain]]:
        abstract_filter = self._seach_filters[type(query_filter)]
        where_filter = abstract_filter.build(query_filter)
        query = self._table.select().where(where_filter)

        if not limit is None:
            query = query.limit(limit)

        if not offset is None:
            query = query.offset(offset)

        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)

        return results

    async def paginated_query(
        self,
        query_filter: Query,
        limit: int,
        next_page_token: Optional[str],
    ) -> Awaitable[Page[Domain]]:
        page_index = 0 if next_page_token is None else int(next_page_token)
        results = await self.query_by(query_filter, limit, limit * page_index)
        return Page(
            next_page_token=str(page_index + 1),
            limit=limit,
            results=results,
        )

    async def remove_by(self, query_filter: QueryFilter) -> Awaitable:
        assert not self._table_filter_type is None
        filter_fields = self._mapper.map(query_filter, dict, self._table_filter_type)
        where_filter = build_and_column_filter(self._table, filter_fields)
        query = self._table.select().where(where_filter)
        records = await self._database.execute(query)

    @abstractmethod
    async def delete_by_id(self, pk_id: Id) -> Awaitable:
        pass

    @abstractmethod
    async def has(self, pk_id: Id) -> Awaitable[bool]:
        pass

    @abstractmethod
    async def find_by_id(self, pk_id: Id) -> Awaitable[Domain]:
        pass

    async def update(
        self, value_filter: QueryFilter, query_filter: QueryFilter
    ) -> Awaitable:
        assert not self._table_filter_type is None
        filter_fields = self._mapper.map(query_filter, dict, self._table_filter_type)
        where_filter = build_and_column_filter(self._table, filter_fields)
        update_fields = self._mapper.map(value_filter, dict, self._table_filter_type)
        query = self._table.update().where(where_filter).values(update_fields)
        await self._database.execute(query=query)

    async def insert_many_raw(self, daos: List[BaseModel]) -> Awaitable:
        columns_name = [
            column_processor.name for column_processor in self._column_processors
        ]

        records = [
            [
                column_processor.processor(getattr(dao, column_processor.name))
                for column_processor in self._column_processors
            ]
            for dao in daos
        ]

        async with self._database.connection() as connection:
            n = 300
            for i in range(0, len(records), n):
                await connection.raw_connection.copy_records_to_table(
                    self._table.name, records=records[i : i + n], columns=columns_name
                )

    def map_many_to(self, records, dao_type, domain_type):
        daos = [dao_type(**record) for record in records]
        results = self._mapper.map_many(daos, domain_type)
        return results

    async def map_over(
        self, iterator: AsyncGenerator[Any, Any]
    ) -> AsyncGenerator[Domain, None]:
        async for record in iterator:
            dao = dao_type(**record)
            result = self._mapper.map(dao, self._domain)
            yield result

    def hydrate_joined_table(self, records, dao_table_pairs):
        def slice_record(record, delta, columns):
            mapped = {}

            for index, column in enumerate(columns):
                mapped[column.name] = record[delta + index]

            return mapped

        for record in records:
            offset = 0
            domains = []
            daos = []

            for (dao_type, domain_type, table) in dao_table_pairs:
                dao = dao_type(**slice_record(record, offset, table.c))
                daos.append(dao)

                domain = self._mapper.map(dao, domain_type, dao_type)
                domains.append(domain)

                offset += len(table.c)

            yield domains, daos


class BaseCrudTableService(CoreCrudTableService[Domain]):
    def __init__(self, database: Database, mapper: Mapper):
        CoreCrudTableService.__init__(self, database, mapper)

        pk = list(self._table.primary_key.columns.values())
        assert (
            len(pk) == 1
        ), f"Crud table service must have single value primary key for table {self._table}"

        self.table_id_name = pk[0].name
        self.table_id = getattr(self._table.c, self.table_id_name)

    async def delete_by_id(self, pk_id: Id) -> Awaitable:
        query = self._table.delete().where(self.table_id == pk_id)
        await self._database.execute(query=query)

    async def has(self, pk_id: Id) -> Awaitable[bool]:
        query = select([self.table_id]).where(self.table_id == pk_id)
        value = await self._database.fetch_one(query=query)
        return not value is None

    async def find_by_id(self, pk_id: Id) -> Awaitable[Domain]:
        query = self._table.select().where(self.table_id == pk_id)
        value = await self._database.fetch_one(query=query)

        if value is None:
            raise RessourceNotFound()

        result = self._mapper.map(self._dao(**value), self._domain)
        return result


class BaseCompositeCrudTableService(CoreCrudTableService[Domain]):
    def __init__(self, database: Database, mapper: Mapper):
        CoreCrudTableService.__init__(self, database, mapper)

        pks = list(self._table.primary_key.columns.values())
        assert len(pks) > 1, f"Compose crud must have composite key for {self._table}"

        self.table_id_names = [pk.name for pk in pks]
        self.table_ids = [
            getattr(self._table.c, table_id_name)
            for table_id_name in self.table_id_names
        ]

    async def delete_by_id(self, pk_id: Id) -> Awaitable:
        identifier = self._mapper.map(pk_id, dict)
        where_filter = self._build_id_filter(identifier)
        query = self._table.delete().where(where_filter)
        await self._database.execute(query=query)

    async def has(self, pk_id: Id) -> Awaitable[bool]:
        identifier = self._mapper.map(pk_id, dict)
        where_filter = self._build_id_filter(identifier)
        query = select([self.table_id]).where(where_filter)
        value = await self._database.fetch_one(query=query)
        return not value is None

    async def find_by_id(self, pk_id: Id) -> Awaitable[Domain]:
        identifier = self._mapper.map(pk_id, dict)
        where_filter = self._build_id_filter(identifier)
        query = self._table.select().where(where_filter)
        value = await self._database.fetch_one(query=query)

        if not value is None:
            result = self._mapper.map(self._dao(**value), self._domain)

            return result

        return None

    def _build_id_filter(self, identifier: dict):
        name = self.table_id_names[0]
        condition = getattr(self._table.c, name) == identifier[name]

        for index in range(0, len(self.table_id_names)):
            name = self.table_id_names[index]
            comparaison = getattr(self._table.c, name) == identifier[name]
            condition = and_(condition, comparaison)

        return condition
