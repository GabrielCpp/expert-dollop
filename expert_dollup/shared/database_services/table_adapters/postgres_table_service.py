from typing import (
    List,
    TypeVar,
    Optional,
    Awaitable,
    Any,
    Dict,
    Type,
    Tuple,
)
from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import and_, func, or_, desc, asc
from sqlalchemy.schema import FetchedValue
from sqlalchemy.sql import select
from databases import Database
from dataclasses import dataclass
from sqlalchemy.dialects import postgresql
from expert_dollup.shared.automapping import Mapper
from ..filters import ExactMatchFilter
from ..page import Page
from ..query_filter import QueryFilter
from ..exceptions import RecordNotFound
from .table_service import TableService, QueryBuilder, WhereFilter

Domain = TypeVar("Domain")
Id = TypeVar("Id")


@dataclass
class TableColumnProcessor:
    name: str
    processor: callable


class PostgresQueryBuilder(QueryBuilder):
    @staticmethod
    def order_by_clause(table, name: str, direction: str):
        assert direction in ("desc", "asc")
        order = desc if direction is "desc" else asc

        return order(getattr(table.c, name))

    def __init__(self, table, mapper, build_filter):
        self._table = table
        self._mapper = mapper
        self._build_filter = build_filter
        self._conditions = []
        self._saved = {}
        self.final_query = None
        self.fields = None
        self.order = None

    def select_fields(self, *names: List[str]) -> "QueryBuilder":
        self.fields = []

        for name in names:
            field = getattr(self._table.c, name)
            self.fields.append(field)

        return self

    def order_by(self, name: str, direction: str) -> "QueryBuilder":
        self.order = PostgresQueryBuilder.order_by_clause(self._table, name, direction)
        return self

    def find_by(self, query_filter: QueryFilter) -> "QueryBuilder":
        where_filter = self._build_filter(query_filter)
        self._conditions.append(where_filter)
        return self

    def find_by_isnot(self, query_filter: QueryFilter) -> "QueryBuilder":
        filter_fields = self._mapper.map(query_filter, dict)

        for name, value in filter_fields.items():
            where_filter = getattr(self._table.c, name).isnot(value)
            self._conditions.append(where_filter)

        return self

    def startwiths(self, query_filter: QueryFilter) -> "QueryBuilder":
        filter_fields = self._mapper.map(query_filter, dict)

        for name, path_filter in filter_fields.items():
            where_filter = getattr(self._table.c, name).like(f"{path_filter}%")
            self._conditions.append(where_filter)

        return self

    def pluck(self, pluck_filter: QueryFilter) -> "QueryBuilder":
        filter_fields = self._mapper.map(pluck_filter, dict)

        for name, values in filter_fields.items():
            where_filter = getattr(self._table.c, name).in_(values)
            self._conditions.append(where_filter)

        return self

    def save(self, name) -> "QueryBuilder":
        self._saved[name] = self._conditions
        self._conditions = []
        return self

    def any_of(self, *names: List[str]) -> "QueryBuilder":
        if len(names) == 0 and len(self._conditions) > 0:
            self._conditions = [or_(*self._conditions)]

        if len(names) > 0:
            merged_conditions = []
            for name in names:
                merged_conditions.extend(self._saved[name])

            self._conditions.append(or_(*names))

        return self

    def all_of(self, *names: List[str]) -> "QueryBuilder":
        if len(names) == 0 and len(self._conditions) > 0:
            self._conditions = [and_(*self._conditions)]

        if len(names) > 0:
            merged_conditions = []
            for name in names:
                merged_conditions.extend(self._saved[name])

            self._conditions.append(and_(*merged_conditions))

        return self

    def finalize(self) -> "QueryBuilder":
        assert (
            len(self._conditions) > 0
        ), "Query builder must contains at leas a condition"

        if len(self._conditions) == 1:
            self.final_query = self._conditions[0]

        self.final_query = and_(*self._conditions)
        return self


class PostgresTableService(TableService[Domain]):
    def __init__(self, database: Database, mapper: Mapper):
        self._database = database
        self._mapper = mapper
        self._table = self.__class__.Meta.table
        self._custom_filters: Dict[Type, callable] = getattr(
            self.__class__.Meta, "custom_filters", dict()
        )
        self._paginator = getattr(self.__class__.Meta, "paginator", lambda _: None)(
            self._table
        )
        self._dao = self.__class__.Meta.dao
        self._domain = self.__class__.Meta.domain
        self._table_filter_type = self.__class__.Meta.table_filter_type
        self._column_processors = self._build_table_raw_processors()

        self.table_id_names = [
            pk.name for pk in self._table.primary_key.columns.values()
        ]
        self.table_ids = [
            getattr(self._table.c, table_id_name)
            for table_id_name in self.table_id_names
        ]

    async def insert(self, domain: Domain) -> Awaitable:
        query = self._table.insert()
        value = self._mapper.map(domain, self._dao).dict()
        await self._database.execute(query=query, values=value)

    async def insert_many(self, domains: List[Domain], bulk=True) -> Awaitable:
        daos = self._mapper.map_many(domains, self._dao)

        if bulk:
            await self._insert_many_raw(daos)
        else:
            query = pg_insert(self._table, [dao.dict() for dao in daos])
            await self._database.execute(query=query)

    async def find_all(self, limit: int = 1000) -> Awaitable[List[Domain]]:
        query = self._table.select().limit(limit)
        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)
        return results

    async def find_all_paginated(
        self, limit: int = 1000, next_page_token: Optional[str] = None
    ) -> Awaitable[Page[Domain]]:
        assert not self._paginator is None, "Paginator required"
        query = self._paginator.build_query(None, limit, next_page_token)
        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)
        new_next_page_token = (
            self._paginator.default_token
            if len(records) == 0
            else self._paginator.encode_record(records[-1])
        )

        return Page(
            next_page_token=new_next_page_token,
            limit=limit,
            results=results,
        )

    async def find_by(
        self,
        query_filter: WhereFilter,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[Tuple[str, str]] = None,
    ) -> Awaitable[List[Domain]]:
        where_filter = self._build_filter(query_filter)
        query = self._table.select().where(where_filter)

        if not limit is None:
            query = query.limit(limit)

        if not offset is None:
            query = query.offset(offset)

        if not order_by is None:
            name, direction = order_by
            query = query.order_by(
                PostgresQueryBuilder.order_by_clause(self._table, name, direction)
            )

        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)

        return results

    async def find_by_paginated(
        self,
        query_filter: WhereFilter,
        limit: int,
        next_page_token: Optional[str] = None,
    ) -> Awaitable[Page[Domain]]:
        assert not self._paginator is None, "Paginator required"
        where_filter = self._build_filter(query_filter)
        query = self._paginator.build_query(where_filter, limit, next_page_token)
        records = await self._database.fetch_all(query=query)
        results = self.map_many_to(records, self._dao, self._domain)

        new_next_page_token = (
            self._paginator.default_token
            if len(records) == 0
            else self._paginator.encode_record(records[-1])
        )

        return Page[Domain](
            next_page_token=new_next_page_token,
            limit=limit,
            results=results,
        )

    async def find_one_by(self, query_filter: WhereFilter) -> Awaitable[List[Domain]]:
        where_filter = self._build_filter(query_filter)
        query = self._table.select().where(where_filter)
        record = await self._database.fetch_one(query=query)

        if record is None:
            raise RecordNotFound()

        result = self._mapper.map(self._dao(**record), self._domain)

        return result

    async def delete_by(self, query_filter: WhereFilter) -> Awaitable:
        where_filter = self._build_filter(query_filter)
        query = self._table.delete().where(where_filter)
        await self._database.execute(query)

    async def count(self, query_filter: Optional[WhereFilter] = None) -> Awaitable[int]:
        if query_filter is None:
            query = select([func.count()]).select_from(self._table)
        else:
            where_filter = self._build_filter(query_filter)
            query = select([func.count()]).select_from(self._table).where(where_filter)

        count = await self._database.fetch_val(query=query)
        return count

    async def delete_by_id(self, pk_id: Id) -> Awaitable:
        where_filter = self._build_id_filter(pk_id)
        query = self._table.delete().where(where_filter)
        await self._database.execute(query=query)

    async def has(self, pk_id: Id) -> Awaitable[bool]:
        where_filter = self._build_id_filter(pk_id)
        query = select(self.table_ids).where(where_filter)
        value = await self._database.fetch_one(query=query)
        return not value is None

    async def find_by_id(self, pk_id: Id) -> Awaitable[Domain]:
        where_filter = self._build_id_filter(pk_id)
        query = self._table.select().where(where_filter)
        value = await self._database.fetch_one(query=query)

        if value is None:
            raise RecordNotFound()

        result = self._mapper.map(self._dao(**value), self._domain)
        return result

    async def update(
        self, value_filter: QueryFilter, query_filter: WhereFilter
    ) -> Awaitable:
        """
        Update records base on query.
        """
        where_filter = self._build_filter(query_filter)
        update_fields = self._mapper.map(value_filter, dict, self._table_filter_type)
        query = self._table.update().where(where_filter).values(update_fields)
        await self._database.execute(query=query)

    def make_record_token(self, domain: Domain) -> str:
        """
        Return next page token for a domain object.
        """
        assert not self._paginator is None, "Paginator required"
        dao = self._mapper.map(domain, self._dao)
        next_page_token = self._paginator.encode_dao(dao)
        return next_page_token

    def map_many_to(self, records: list, dao_type: BaseModel, domain_type: Domain):
        """
        Remap a list of records to it domain equivalent.
        """
        daos = [dao_type(**record) for record in records]
        results = self._mapper.map_many(daos, domain_type)
        return results

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

    def get_builder(self) -> QueryBuilder:
        return PostgresQueryBuilder(self._table, self._mapper, self._build_filter)

    async def fetch_all_records(self, builder: QueryBuilder) -> dict:
        query = select(builder.fields or []).where(builder.final_query)
        records = await self._database.fetch_all(query=query)
        return records

    async def _insert_many_raw(self, daos: List[BaseModel]) -> Awaitable:
        """
        Postgres specific bulk insert of daos
        """
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

    def _build_filter(self, query_filter: QueryFilter):
        query_type = type(query_filter)

        if query_type is PostgresQueryBuilder:
            assert (
                not query_filter.final_query is None
            ), "Query builder query must be finalized"
            return query_filter.final_query

        if query_type in self._custom_filters:
            return self._custom_filters[query_type](query_filter, self._mapper)

        assert not self._table_filter_type is None, "Table filter is missing."
        filter_fields = self._mapper.map(query_filter, dict, self._table_filter_type)
        where_filter = ExactMatchFilter.build_and_column_filter(
            self._table, filter_fields
        )

        return where_filter

    def _build_id_filter(self, pk_id):
        if len(self.table_ids) == 1:
            return self.table_ids[0] == pk_id

        identifier = self._mapper.map(pk_id, dict)
        name = self.table_id_names[0]
        condition = getattr(self._table.c, name) == identifier[name]

        for index in range(0, len(self.table_id_names)):
            name = self.table_id_names[index]
            comparaison = getattr(self._table.c, name) == identifier[name]
            condition = and_(condition, comparaison)

        return condition

    def _build_table_raw_processors(self) -> List[TableColumnProcessor]:
        noop = lambda x: x
        dialect = postgresql.dialect()

        return [
            TableColumnProcessor(
                name=column.name, processor=column.type.bind_processor(dialect) or noop
            )
            for column in self._table.c
            if not isinstance(column.server_default, FetchedValue)
        ]
