from typing import (
    List,
    TypeVar,
    Optional,
    Dict,
    Type,
    Union,
)
from pydantic import BaseModel, ConstrainedStr
from pydantic.fields import ModelField
from inspect import isclass
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import (
    MetaData,
    and_,
    func,
    desc,
    asc,
    Table,
    Column,
    String,
    Boolean,
    DateTime,
    Integer,
    text,
)
from sqlalchemy.sql import select
from sqlalchemy.dialects.postgresql import insert as pg_insert, ARRAY
from sqlalchemy.dialects import postgresql
from expert_dollup.shared.automapping import Mapper
from ..adapter_interfaces import (
    CollectionService,
    QueryBuilder,
    WhereFilter,
    DbConnection,
)
from ..query_filter import QueryFilter
from ..exceptions import RecordNotFound
from ..batch_helper import batch
from ..json_serializer import JsonSerializer
from ..collection_mapper import CollectionMapper
from ..db_agnotist_query_builder import DbAgnotistQueryBuilder

NoneType = type(None)


import sqlalchemy.types as types


class UUIDWrap(types.TypeDecorator):
    """
    Wrap asyncpg uuid to ensure they are converted to python uuid
    """

    impl = postgresql.UUID(as_uuid=True)

    cache_ok = True

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        return UUID(bytes=value.bytes)


class PostgresColumnBuilder:
    def __init__(self):
        self._column_builder = {
            Union: self._build_union,
            Dict: self._build_dict,
            dict: self._build_dict,
            list: self._build_list,
            UUID: self._build_uuid,
            int: self._build_int,
            str: self._build_str,
            "ConstrainedStrValue": self._build_str,
            ConstrainedStr: self._build_str,
            bool: self._build_bool,
            datetime: self._build_datetime,
            BaseModel: self._build_object,
        }

    def build(self, meta: Type, schema: dict, field: ModelField):
        options = {"nullable": field.required}
        db_type = self._build_column_type(schema, field, options)

        if field.name == meta.pk or (
            isinstance(meta.pk, tuple) and field.name in meta.pk
        ):
            options["primary_key"] = True

        return Column(field.name, db_type, **options)

    def _build_column_type(self, schema: dict, field, options) -> Column:
        type_origin = getattr(field.outer_type_, "__origin__", field.type_)
        type_args = getattr(field.outer_type_, "__args__", [])

        if type_origin == Union and len(type_args) == 2 and NoneType in type_args:
            type_origin = [
                type_arg for type_arg in type_args if not type_arg is NoneType
            ][0]
            type_args = []

        elif isclass(type_origin) and issubclass(type_origin, BaseModel):
            type_origin = BaseModel
            type_args = []

        assert (
            type_origin in self._column_builder
            or type_origin.__name__ in self._column_builder
        ), f"Unsupported column type for {type_origin}"

        build_type = self._column_builder[
            type_origin if type_origin in self._column_builder else type_origin.__name__
        ]

        return build_type(schema, type_args)

    def _build_int(self, schema: dict, type_args: List[Type]):
        return Integer

    def _build_str(self, schema: dict, type_args: List[Type]):
        if "maxLength" in schema:
            return String(schema["maxLength"])

        return String

    def _build_uuid(self, schema: dict, type_args: List[Type]):
        return UUIDWrap()

    def _build_bool(self, schema: dict, type_args: List[Type]):
        return Boolean

    def _build_datetime(self, schema: dict, type_args: List[Type]):
        return DateTime(timezone=True)

    def _build_object(self, schema: dict, type_args: List[Type]):
        return self._make_json_column_type()

    def _build_union(self, schema: dict, type_args: List[Type]):
        return self._make_json_column_type()

    def _build_dict(self, schema: dict, type_args: List[Type]):
        return self._make_json_column_type()

    def _build_list(self, schema: dict, type_args: List[Type]):
        if type_args[0] is str:
            return postgresql.ARRAY(String, dimensions=1)

        if type_args[0] is UUID:
            return ARRAY(UUIDWrap(), dimensions=1)

        return self._make_json_column_type()

    def _make_json_column_type(self) -> postgresql.JSON:
        column_type = postgresql.JSON(none_as_null=True)
        return column_type


class PostgresConnection(DbConnection):
    def __init__(self, connection_string: str, **kwargs):
        self.metadata = MetaData()
        self.tables: Dict[Type, Table] = {}
        self._engine = create_async_engine(
            connection_string,
            json_serializer=JsonSerializer.encode,
            json_deserializer=JsonSerializer.decode,
            **kwargs,
        )

    def get_collection_service(self, meta: Type, mapper: Mapper):
        return PostgresTableService(meta, self.tables, self._engine, mapper)

    def load_metadatas(self, dao_types):
        column_builder = PostgresColumnBuilder()

        for dao_type in dao_types:
            if not hasattr(dao_type, "Meta"):
                continue

            schema = dao_type.schema()
            assert schema.get("type") == "object"
            assert "properties" in schema

            columns = [
                column_builder.build(
                    dao_type.Meta,
                    schema["properties"][field.name],
                    field,
                )
                for field in dao_type.__fields__.values()
            ]

            if hasattr(dao_type.Meta, "version"):
                columns.append(Column("_version", Integer, nullable=False))

            table_name = schema["title"]
            table = Table(table_name, self.metadata, *columns)
            self.tables[dao_type] = table

    async def truncate_db(self, tables: Optional[List[str]] = None):
        async with self._engine.begin() as con:
            if tables is None:
                tables = [table.name for table in self.tables.values()]

            for table in tables:
                await con.execute(text(f'ALTER TABLE "{table}" DISABLE TRIGGER ALL;'))
                await con.execute(text(f"DELETE FROM {table};"))
                await con.execute(text(f'ALTER TABLE "{table}" ENABLE TRIGGER ALL;'))

    async def drop_db(self):
        async with self._engine.begin() as conn:
            await conn.execute(text(f"DROP SCHEMA public CASCADE;"))
            await conn.execute(text(f"CREATE SCHEMA public;"))

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        await self._engine.dispose()

    @property
    def is_connected(self) -> bool:
        return True


BATCH_SIZE = 1000
SUPPORTED_OPS = {
    "==": lambda lhs, rhs: lhs == rhs,
    "<": lambda lhs, rhs: lhs < rhs,
    "in": lambda lhs, rhs: lhs.in_(rhs),
    "startwiths": lambda lhs, rhs: lhs.like(f"{rhs}%"),
}


class QueryCompiler:
    @staticmethod
    def compile_query(builder, table):
        query = (
            table.select()
            if builder._selections is None
            else select([getattr(table.c, name) for name in builder._selections])
        )

        where_filter = QueryCompiler.build_where_filter(builder, table)

        if not where_filter is None:
            query = query.where(where_filter)

        if not builder._orders is None:
            ordering = []

            for column_name, direction in builder._orders:
                assert direction in ("desc", "asc")
                apply_order = desc if direction == "desc" else asc
                ordering.append(apply_order(getattr(table.c, column_name)))

            query = query.order_by(*ordering)

        if not builder._max_records is None:
            query = query.limit(builder._max_records)

        return query

    @staticmethod
    def build_where_filter(builder, table):
        where_filter = None

        for (column_name, op, value) in builder._wheres:
            apply_op = SUPPORTED_OPS[op]
            operator = apply_op(getattr(table.c, column_name), value)

            if where_filter is None:
                where_filter = operator
            else:
                where_filter = and_(where_filter, operator)

        return where_filter

    @staticmethod
    def build_and_column_filter(table, fields: dict):
        condition = None

        for column_name, value in fields.items():
            if condition is None:
                condition = getattr(table.c, column_name) == value
            else:
                condition = and_(condition, getattr(table.c, column_name) == value)

        return condition


Domain = TypeVar("Domain")
Id = TypeVar("Id")


class PostgresTableService(CollectionService[Domain]):
    def __init__(
        self,
        meta: Type,
        tables: Dict[Type, Table],
        engine,
        mapper: Mapper,
    ):
        self._dao = meta.dao
        self._domain = meta.domain
        self._mapper = mapper
        self._database = engine
        self._table = tables.get(meta.dao)
        self._dao_mapper = CollectionMapper(
            mapper,
            meta.domain,
            meta.dao,
            getattr(meta.dao.Meta, "version", None),
            getattr(meta.dao.Meta, "version_mappers", {}),
            record_to_dict=lambda r: r._asdict(),
        )

        self.table_id_names = [
            pk.name for pk in self._table.primary_key.columns.values()
        ]

        self.table_ids = [
            getattr(self._table.c, table_id_name)
            for table_id_name in self.table_id_names
        ]

    @property
    def domain(self) -> Type:
        return self._domain

    @property
    def dao(self) -> Type:
        return self._dao

    async def insert(self, domain: Domain):
        value = self._dao_mapper.map_to_dict(domain)
        query = self._table.insert().values(value)

        await self._execute(query)

    async def insert_many(self, domains: List[Domain]):
        dicts = self._dao_mapper.map_many_to_dict(domains)

        for dicts_batch in batch(dicts, BATCH_SIZE):
            query = pg_insert(self._table, dicts_batch)
            await self._execute(query)

    async def upserts(self, domains: List[Domain]) -> None:
        if len(domains) == 0:
            return

        dicts = self._dao_mapper.map_many_to_dict(domains)
        constraint = f"{self._table.name}_pkey"

        for items in batch(dicts, BATCH_SIZE):
            query = pg_insert(self._table, items)
            set_ = {c.name: c for c in query.excluded if not c.primary_key}
            query = query.on_conflict_do_update(
                constraint=constraint,
                set_=set_,
            )

            await self._execute(query=query)

    async def find_all(self, limit: int = 1000) -> List[Domain]:
        query = self._table.select().limit(limit)
        records = await self._fetch_all(query=query)
        results = self._dao_mapper.map_many_to_domain(records)
        return results

    async def find_by(self, query_filter: WhereFilter) -> List[Domain]:
        query = self._build_query(query_filter)
        records = await self._fetch_all(query=query)
        results = self._dao_mapper.map_many_to_domain(records)

        return results

    async def find_one_by(self, query_filter: WhereFilter) -> Domain:
        query = self._build_query(query_filter)
        record = await self._fetch_one(query)

        if record is None:
            raise RecordNotFound()

        result = self._dao_mapper.map_to_domain(record)

        return result

    async def delete_by(self, query_filter: WhereFilter):
        where_filter = self._build_filter(query_filter)
        query = self._table.delete().where(where_filter)
        await self._execute(query)

    async def count(self, query_filter: Optional[WhereFilter] = None) -> int:
        query = select([func.count()]).select_from(self._table)

        if not query_filter is None:
            where_filter = self._build_filter(query_filter)
            query = query.where(where_filter)

        count = await self._fetch_val(query=query)
        return count

    async def delete_by_id(self, pk_id: Id):
        where_filter = self._build_id_filter(pk_id)
        query = self._table.delete().where(where_filter)
        await self._execute(query=query)

    async def exists(self, query_filter: WhereFilter) -> bool:
        query = self._build_query(query_filter)
        record = await self._fetch_one(query)
        return not record is None

    async def has(self, pk_id: Id) -> bool:
        where_filter = self._build_id_filter(pk_id)
        query = select(self.table_ids).where(where_filter)
        value = await self._fetch_one(query=query)
        return not value is None

    async def find_by_id(self, pk_id: Id) -> Domain:
        where_filter = self._build_id_filter(pk_id)
        query = self._table.select().where(where_filter)
        record = await self._fetch_one(query=query)

        if record is None:
            raise RecordNotFound()

        result = self._dao_mapper.map_to_domain(record)
        return result

    async def update(self, value_filter: QueryFilter, query_filter: WhereFilter):
        where_filter = self._build_filter(query_filter)
        update_fields = self._mapper.map(value_filter, dict, value_filter.__class__)
        query = self._table.update().where(where_filter).values(update_fields)
        await self._execute(query)

    def get_builder(self) -> QueryBuilder:
        return DbAgnotistQueryBuilder()

    async def fetch_all_records(self, builder: WhereFilter) -> List[dict]:
        query = self._build_query(builder)
        records = await self._fetch_all(query=query)
        return [record._asdict() for record in records]

    async def bulk_insert(self, daos: List[BaseModel]):
        columns_name = [column.name for column in self._table.c]
        records = []

        for dao in daos:
            d = self._dao_mapper.add_version_to_dao(dao)
            records.append([d[column_name] for column_name in columns_name])

        async with self._database.connect() as connection:
            conn = await connection.get_raw_connection()
            await conn.driver_connection.copy_records_to_table(
                self._table.name, records=records, columns=columns_name
            )

    def _build_query(self, builder: WhereFilter):
        if isinstance(builder, DbAgnotistQueryBuilder):
            return QueryCompiler.compile_query(builder, self._table)

        return self._table.select().where(self._build_filter(builder))

    def _build_filter(self, builder: WhereFilter):
        if isinstance(builder, DbAgnotistQueryBuilder):
            return QueryCompiler.build_where_filter(builder, self._table)

        filter_fields = self._mapper.map(builder, dict, builder.__class__)
        where_filter = QueryCompiler.build_and_column_filter(self._table, filter_fields)
        return where_filter

    def _build_id_filter(self, pk_id):
        if len(self.table_ids) == 1:
            return self.table_ids[0] == pk_id

        identifier = self._mapper.map(pk_id, dict, pk_id.__class__)
        name = self.table_id_names[0]
        condition = getattr(self._table.c, name) == identifier[name]

        for name in self.table_id_names:
            comparaison = getattr(self._table.c, name) == identifier[name]
            condition = and_(condition, comparaison)

        return condition

    async def _fetch_all(self, query) -> List[dict]:
        async with self._database.begin() as conn:
            result = await conn.execute(query)
            return result.fetchall()

    async def _fetch_one(self, query) -> List[dict]:
        async with self._database.begin() as conn:
            result = await conn.execute(query)
            return result.fetchone()

    async def _fetch_val(self, query) -> List[dict]:
        async with self._database.begin() as conn:
            result = await conn.execute(query)
            row = result.fetchone()
            return row if row is None else row[0]

    async def _execute(self, query):
        async with self._database.begin() as conn:
            return await conn.execute(query)
