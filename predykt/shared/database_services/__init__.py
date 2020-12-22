from abc import ABC, abstractmethod
from typing import List, TypeVar, Optional, Generic, Awaitable
from sqlalchemy.sql import select
from sqlalchemy import and_
from databases import Database
from predykt.shared.automapping import Mapper

Domain = TypeVar('Domain')
Id = TypeVar('Id')


class AbstractFilter(ABC):
    @abstractmethod
    def build(self):
        pass


class AttributeQuery(Generic[Domain]):
    pass


class BaseCrudTableService(Generic[Domain]):
    def __init__(self, database: Database, mapper: Mapper):
        self._database = database
        self._mapper = mapper
        self._table = self.__class__.Meta.table
        self._dao = self.__class__.Meta.dao
        self._domain = self.__class__.Meta.domain
        self._seach_filters = self.__class__.Meta.seach_filters or {}

        pk = list(self._table.primary_key.columns.values())
        assert len(pk) == 1

        self.table_id_name = pk[0].name
        self.table_id = getattr(self._table.c, self.table_id_name)

    async def insert(self, domain: Domain) -> Awaitable:
        query = self._table.insert()
        value = self._mapper.map(domain, self._dao).dict()
        await self._database.execute(query=query, values=value)

    async def insert_many(self, domains: List[Domain]) -> Awaitable:
        query = self._table.insert()
        values = self._mapper.map_many(
            domains,
            self._dao,
            after=lambda x: x.dict()
        )

        await self._database.execute(query=query, values=values)

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

        if not value is None:
            result = self._mapper.map(
                self._dao(**value),
                self._domain
            )

            return result

        return None

    async def find_by(self, query_filter: AttributeQuery[Domain], limit: Optional[int] = None) -> Awaitable[List[Domain]]:
        concrete_filter = self._mapper.map(
            query_filter,
            AbstractFilter
        )

        where_filter = concrete_filter.build()
        query = self._table.select().where(where_filter)
        values = await self._database.fetch_all(query=query)
        results = self._mapper.map_many(
            values,
            self._domain,
            after=lambda x: x.dict()
        )

        return results

    async def update_by_id(self, domain: Domain) -> Awaitable:
        value = self._mapper.map(
            value,
            self._dao,
            after=lambda x: x.dict()
        )

        query = self._table.update().where(
            self.table_id == value[self.table_id_name]).values(**value)

        await self._database.execute(query=query)


class BaseCompositeCrudTableService(Generic[Domain]):
    def __init__(self, database: Database, mapper: Mapper):
        self._database = database
        self._mapper = mapper
        self._table = self.__class__.Meta.table
        self._dao = self.__class__.Meta.dao
        self._domain = self.__class__.Meta.domain
        self._seach_filters = self.__class__.Meta.seach_filters or {}

        pks = list(self._table.primary_key.columns.values())
        assert len(pks) > 1

        self.table_id_names = [pk.name for pk in pks]
        self.table_ids = [getattr(self._table.c, table_id_name)
                          for table_id_name in self.table_id_names]

    async def insert(self, domain: Domain) -> Awaitable:
        query = self._table.insert()
        value = self._mapper.map(domain, self._dao).dict()
        await self._database.execute(query=query, values=value)

    async def insert_many(self, domains: List[Domain]) -> Awaitable:
        query = self._table.insert()
        values = self._mapper.map_many(
            domains,
            self._dao,
            after=lambda x: x.dict()
        )

        await self._database.execute(query=query, values=values)

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
            result = self._mapper.map(
                self._dao(**value),
                self._domain
            )

            return result

        return None

    async def find_by(self, query_filter: AttributeQuery[Domain], limit: Optional[int] = None) -> Awaitable[List[Domain]]:
        concrete_filter = self._mapper.map(
            query_filter,
            AbstractFilter
        )

        where_filter = concrete_filter.build()
        query = self._table.select().where(where_filter)
        values = await self._database.fetch_all(query=query)
        results = self._mapper.map_many(
            values,
            self._domain,
            after=lambda x: x.dict()
        )

        return results

    async def update_by_id(self, domain: Domain) -> Awaitable:
        value = self._mapper.map(
            value,
            self._dao,
            after=lambda x: x.dict()
        )

        where_filter = self._build_id_filter(value)
        query = self._table.update().where(where_filter).values(**value)

        await self._database.execute(query=query)

    def _build_id_filter(self, identifier: dict):
        name = self.table_id_names[0]
        condition = getattr(self._table.c, name) == identifier[name]

        for index in range(0, len(self.table_id_names)):
            name = self.table_id_names[index]
            comparaison = getattr(
                self._table.c, name) == identifier[name]
            condition = and_(condition, comparaison)

        return condition
