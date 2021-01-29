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
from sqlalchemy.sql import select
from sqlalchemy import and_
from databases import Database
from expert_dollup.shared.automapping import Mapper
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


class BaseCrudTableService(Generic[Domain]):
    def __init__(self, database: Database, mapper: Mapper):
        self._database = database
        self._mapper = mapper
        self._table = self.__class__.Meta.table
        self._dao = self.__class__.Meta.dao
        self._domain = self.__class__.Meta.domain
        self._table_filter_type = self.__class__.Meta.table_filter_type
        self._seach_filters = self.__class__.Meta.seach_filters or {}

        pk = list(self._table.primary_key.columns.values())
        assert (
            len(pk) == 1
        ), f"Crub table service must have single value primary key for table {self._table}"

        self.table_id_name = pk[0].name
        self.table_id = getattr(self._table.c, self.table_id_name)

    async def insert(self, domain: Domain) -> Awaitable:
        query = self._table.insert()
        value = self._mapper.map(domain, self._dao).dict()
        await self._database.execute(query=query, values=value)

    async def insert_many(self, domains: List[Domain]) -> Awaitable:
        query = self._table.insert()
        values = self._mapper.map_many(domains, self._dao, after=lambda x: x.dict())
        await self._database.execute_many(query=query, values=values)

    async def delete_by_id(self, pk_id: Id) -> Awaitable:
        query = self._table.delete().where(self.table_id == pk_id)
        await self._database.execute(query=query)

    async def has(self, pk_id: Id) -> Awaitable[bool]:
        query = select([self.table_id]).where(self.table_id == pk_id)
        value = await self._database.fetch_one(query=query)
        return not value is None

    async def find_all(self, limit: int = 1000) -> Awaitable[List[Domain]]:
        query = self._table.select().limit(limit)
        records = await self._database.fetch_all(query=query)
        results = self._map_many_to(records, self._dao, self._domain)
        return results

    async def find_by_id(self, pk_id: Id) -> Awaitable[Domain]:
        query = self._table.select().where(self.table_id == pk_id)
        value = await self._database.fetch_one(query=query)

        if not value is None:
            result = self._mapper.map(self._dao(**value), self._domain)

            return result

        return None

    async def query_by(
        self, query_filter: Query, limit: Optional[int] = None
    ) -> Awaitable[List[Domain]]:
        abstract_filter = self._seach_filters[type(query_filter)]
        where_filter = abstract_filter.build(query_filter)
        query = self._table.select().where(where_filter)
        records = await self._database.fetch_all(query=query)
        results = self._map_many_to(records, self._dao, self._domain)

        return results

    async def find_by(
        self, query_filter: QueryFilter, limit: Optional[int] = None
    ) -> Awaitable[List[Domain]]:
        filter_fields = (
            query_filter
            if self._table_filter_type is None
            else self._mapper.map(query_filter, dict, self._table_filter_type)
        )

        where_filter = build_and_column_filter(self._table, filter_fields)
        query = self._table.select().where(where_filter)
        records = await self._database.fetch_all(query=query)
        results = self._map_many_to(records, self._dao, self._domain)

        return results

    async def update_by_id(self, domain: Domain) -> Awaitable:
        value = self._mapper.map(value, self._dao, after=lambda x: x.dict())

        query = (
            self._table.update()
            .where(self.table_id == value[self.table_id_name])
            .values(**value)
        )

        await self._database.execute(query=query)

    def _map_many_to(self, records, dao_type, domain_type):
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


class BaseCompositeCrudTableService(Generic[Domain]):
    def __init__(self, database: Database, mapper: Mapper):
        self._database = database
        self._mapper = mapper
        self._table = self.__class__.Meta.table
        self._dao = self.__class__.Meta.dao
        self._domain = self.__class__.Meta.domain
        self._seach_filters = self.__class__.Meta.seach_filters or {}

        pks = list(self._table.primary_key.columns.values())
        assert len(pks) > 1, f"Compose crud must have composite key for {self._table}"

        self.table_id_names = [pk.name for pk in pks]
        self.table_ids = [
            getattr(self._table.c, table_id_name)
            for table_id_name in self.table_id_names
        ]

    async def insert(self, domain: Domain) -> Awaitable:
        query = self._table.insert()
        value = self._mapper.map(domain, self._dao).dict()
        await self._database.execute(query=query, values=value)

    async def insert_many(self, domains: List[Domain]) -> Awaitable:
        query = self._table.insert()
        values = self._mapper.map_many(domains, self._dao, after=lambda x: x.dict())

        await self._database.execute_many(query=query, values=values)

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

    async def find_by(
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
        daos = [self._dao(**value) for value in values]
        results = self._mapper.map_many(daos, self._domain)

        return results

    async def paginated_find_by(
        self,
        query_filter: Query,
        limit: int,
        next_page_token: Optional[str],
    ) -> Awaitable[Page[Domain]]:
        page_index = 0 if next_page_token is None else int(next_page_token)
        results = await self.find_by(query_filter, limit, limit * page_index)
        return Page(
            next_page_token=str(page_index + 1),
            limit=limit,
            results=results,
        )

    async def update_by_id(self, domain: Domain) -> Awaitable:
        value = self._mapper.map(value, self._dao, after=lambda x: x.dict())

        where_filter = self._build_id_filter(value)
        query = self._table.update().where(where_filter).values(**value)

        await self._database.execute(query=query)

    def _build_id_filter(self, identifier: dict):
        name = self.table_id_names[0]
        condition = getattr(self._table.c, name) == identifier[name]

        for index in range(0, len(self.table_id_names)):
            name = self.table_id_names[index]
            comparaison = getattr(self._table.c, name) == identifier[name]
            condition = and_(condition, comparaison)

        return condition
