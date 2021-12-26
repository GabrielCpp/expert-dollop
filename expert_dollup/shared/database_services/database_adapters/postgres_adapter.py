from typing import (
    List,
    TypeVar,
    Optional,
    Awaitable,
    Dict,
    Type,
    Tuple,
    Union,
)
from pydantic import BaseModel, ConstrainedStr
from pydantic.fields import ModelField
from dataclasses import dataclass
from inspect import isclass
from uuid import UUID
from datetime import datetime
from databases import Database
from databases.backends.postgres import PostgresBackend
from sqlalchemy import (
    MetaData,
    create_engine,
    and_,
    func,
    or_,
    desc,
    asc,
    Table,
    Column,
    String,
    Boolean,
    DateTime,
    Integer,
)
from sqlalchemy.schema import FetchedValue
from sqlalchemy.sql import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.interfaces import Dialect
from expert_dollup.shared.automapping import Mapper
from ..adapter_interfaces import (
    CollectionService,
    QueryBuilder,
    WhereFilter,
    DbConnection,
)
from ..page import Page
from ..query_filter import QueryFilter
from ..exceptions import RecordNotFound
from ..batch_helper import batch
from ..json_serializer import JsonSerializer


NoneType = type(None)


def create_postgres_dialect():
    dialect = postgresql.dialect(
        json_deserializer=lambda x: x,
        json_serializer=lambda x: x,
        paramstyle="pyformat",
    )

    dialect.implicit_returning = True
    dialect.supports_native_enum = True
    dialect.supports_smallserial = True  # 9.2+
    dialect._backslash_escapes = False
    dialect.supports_sane_multi_rowcount = True  # psycopg 2.0.9+
    dialect._has_native_hstore = True
    dialect.supports_native_decimal = True

    return dialect


class AiopgBackendWithCustomSerializer(PostgresBackend):
    def _get_dialect(self) -> Dialect:
        return create_postgres_dialect()


Database.SUPPORTED_BACKENDS[
    "postgresql"
] = "expert_dollup.shared.database_services.database_adapters.postgres_adapter:AiopgBackendWithCustomSerializer"


class PostgresColumnBuilder:
    def __init__(self):
        self._column_builder = {
            Union: self._build_union,
            Dict: self._build_dict,
            dict: self._build_dict,
            List: self._build_list,
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
        db_type = self._build_column_type(schema, field.type_)
        options = {"nullable": field.required}

        if field.name == meta.pk or (
            isinstance(meta.pk, tuple) and field.name in meta.pk
        ):
            options["primary_key"] = True

        return Column(field.name, db_type, **options)

    def _build_column_type(self, schema: dict, field_type: Type) -> Column:
        type_origin = getattr(field_type, "__origin__", field_type)
        type_args = getattr(field_type, "__args__", [])

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
        return postgresql.UUID(as_uuid=True)

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

        return self._make_json_column_type()

    def _make_json_column_type(self) -> postgresql.JSON:
        column_type = postgresql.JSON(none_as_null=True)
        return column_type


class PostgresConnection(DbConnection):
    def __init__(self, connection_string: str, **kwargs):
        self.connection_string = connection_string
        self._database = Database(
            connection_string,
            init=PostgresConnection._init_connection,
            **kwargs,
        )
        self.metadata = MetaData()
        self.tables: Dict[Type, Table] = {}

    def get_collection_service(self, meta: Type, mapper: Mapper):
        return PostgresTableService(meta, self.tables, self._database, mapper)

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
        engine = create_engine(self.connection_string)
        con = engine.connect()
        trans = con.begin()

        if tables is None:
            meta = MetaData()
            meta.reflect(bind=engine)

            for table in meta.sorted_tables:
                con.execute(f'ALTER TABLE "{table.name}" DISABLE TRIGGER ALL;')
                con.execute(table.delete())
                con.execute(f'ALTER TABLE "{table.name}" ENABLE TRIGGER ALL;')
        else:
            for table in tables:
                con.execute(f'ALTER TABLE "{table}" DISABLE TRIGGER ALL;')
                con.execute(f"DELETE FROM {table};")
                con.execute(f'ALTER TABLE "{table}" ENABLE TRIGGER ALL;')

        trans.commit()

    async def drop_db(self):
        engine = create_engine(self.connection_string)
        meta = MetaData()
        meta.reflect(bind=engine)
        for tbl in reversed(meta.sorted_tables):
            tbl.drop(engine)

    async def connect(self) -> None:
        await self._database.connect()

    async def disconnect(self) -> None:
        await self._database.disconnect()

    @property
    def is_connected(self) -> bool:
        return self._database.is_connected

    @staticmethod
    async def _init_connection(conn):
        await conn.set_type_codec(
            "json",
            encoder=JsonSerializer.encode,
            decoder=JsonSerializer.decode,
            schema="pg_catalog",
        )

        await conn.set_type_codec(
            "json",
            encoder=lambda x: JsonSerializer.encode(x).encode("utf8"),
            decoder=lambda x: JsonSerializer.decode(x.decode("utf8")),
            schema="pg_catalog",
            format="binary",
        )


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
        order = desc if direction == "desc" else asc

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
        filter_fields = self._mapper.map(query_filter, dict, query_filter.__class__)

        for name, value in filter_fields.items():
            where_filter = getattr(self._table.c, name).isnot(value)
            self._conditions.append(where_filter)

        return self

    def startwiths(self, query_filter: QueryFilter) -> "QueryBuilder":
        filter_fields = self._mapper.map(query_filter, dict, query_filter.__class__)

        for name, path_filter in filter_fields.items():
            where_filter = getattr(self._table.c, name).like(f"{path_filter}%")
            self._conditions.append(where_filter)

        return self

    def pluck(self, pluck_filter: QueryFilter) -> "QueryBuilder":
        filter_fields = self._mapper.map(pluck_filter, dict, pluck_filter.__class__)

        for name, values in filter_fields.items():
            assert (
                len(values) <= 1000
            ), f"Len of batch must be less than 1000, now {len(values)}"
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


class PostgresTableService(CollectionService[Domain]):
    def __init__(
        self,
        meta: Type,
        tables: Dict[Type, Table],
        connector: Database,
        mapper: Mapper,
    ):
        self._mapper = mapper
        self._dao = meta.dao
        self._domain = meta.domain
        self._paginator_factory = getattr(meta, "paginator", lambda _: None)
        self._version = getattr(self._dao.Meta, "version", None)
        self._version_mappers = getattr(self._dao.Meta, "version_mappers", {})
        self._database = connector
        self._table = tables.get(self._dao)
        self._paginator = self._paginator_factory(self._table)
        self._column_processors = self._build_table_raw_processors()

        self.table_id_names = [
            pk.name for pk in self._table.primary_key.columns.values()
        ]

        self.table_ids = [
            getattr(self._table.c, table_id_name)
            for table_id_name in self.table_id_names
        ]

    async def insert(self, domain: Domain):
        query = self._table.insert()
        value = self._map_to_dict(domain)
        await self._database.execute(query=query, values=value)

    async def insert_many(self, domains: List[Domain], bulk=True):
        dicts = self._map_many_to_dict(domains)

        if bulk:
            await self._insert_many_raw(dicts)
        else:
            query = pg_insert(self._table, dicts)
            await self._database.execute(query=query)

    async def upserts(self, domains: List[Domain]) -> None:
        if len(domains) == 0:
            return

        dicts = self._map_many_to_dict(domains)
        constraint = f"{self._table.name}_pkey"

        for items in batch(dicts, 1000):
            query = pg_insert(self._table, items)
            set_ = {c.name: c for c in query.excluded if not c.primary_key}
            query = query.on_conflict_do_update(
                constraint=constraint,
                set_=set_,
            )
            await self._database.execute(query=query)

    async def find_all(self, limit: int = 1000) -> List[Domain]:
        query = self._table.select().limit(limit)
        records = await self._database.fetch_all(query=query)
        results = self._map_many_to_domain(records)
        return results

    async def find_all_paginated(
        self, limit: int = 1000, next_page_token: Optional[str] = None
    ) -> Page[Domain]:
        assert not self._paginator is None, "Paginator required"
        query = self._paginator.build_query(None, limit, next_page_token)
        records = await self._database.fetch_all(query=query)
        results = self._map_many_to_domain(records)
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
    ) -> List[Domain]:
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
        results = self._map_many_to_domain(records)

        return results

    async def find_by_paginated(
        self,
        query_filter: WhereFilter,
        limit: int,
        next_page_token: Optional[str] = None,
    ) -> Page[Domain]:
        assert not self._paginator is None, "Paginator required"
        where_filter = self._build_filter(query_filter)
        query = self._paginator.build_query(where_filter, limit, next_page_token)
        records = await self._database.fetch_all(query=query)
        results = self._map_many_to_domain(records)

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

    async def find_one_by(self, query_filter: WhereFilter) -> Domain:
        where_filter = self._build_filter(query_filter)
        query = self._table.select().where(where_filter)
        record = await self._database.fetch_one(query=query)

        if record is None:
            raise RecordNotFound()

        result = self._map_to_domain(record)

        return result

    async def delete_by(self, query_filter: WhereFilter):
        where_filter = self._build_filter(query_filter)
        query = self._table.delete().where(where_filter)
        await self._database.execute(query)

    async def count(self, query_filter: Optional[WhereFilter] = None) -> int:
        if query_filter is None:
            query = select([func.count()]).select_from(self._table)
        else:
            where_filter = self._build_filter(query_filter)
            query = select([func.count()]).select_from(self._table).where(where_filter)

        count = await self._database.fetch_val(query=query)
        return count

    async def delete_by_id(self, pk_id: Id):
        where_filter = self._build_id_filter(pk_id)
        query = self._table.delete().where(where_filter)
        await self._database.execute(query=query)

    async def has(self, pk_id: Id) -> bool:
        where_filter = self._build_id_filter(pk_id)
        query = select(self.table_ids).where(where_filter)
        value = await self._database.fetch_one(query=query)
        return not value is None

    async def find_by_id(self, pk_id: Id) -> Domain:
        where_filter = self._build_id_filter(pk_id)
        query = self._table.select().where(where_filter)
        record = await self._database.fetch_one(query=query)

        if record is None:
            raise RecordNotFound()

        result = self._map_to_domain(record)
        return result

    async def update(self, value_filter: QueryFilter, query_filter: WhereFilter):
        where_filter = self._build_filter(query_filter)
        update_fields = self._mapper.map(value_filter, dict, value_filter.__class__)
        query = self._table.update().where(where_filter).values(update_fields)
        await self._database.execute(query=query)

    def make_record_token(self, domain: Domain) -> str:
        assert not self._paginator is None, "Paginator required"
        dao = self._mapper.map(domain, self._dao)
        next_page_token = self._paginator.encode_dao(dao)
        return next_page_token

    def get_builder(self) -> QueryBuilder:
        return PostgresQueryBuilder(self._table, self._mapper, self._build_filter)

    async def fetch_all_records(self, builder: QueryBuilder) -> dict:
        query = select(builder.fields or []).where(builder.final_query)
        records = await self._database.fetch_all(query=query)
        return records

    def _map_to_dict(self, domain: Domain) -> dict:
        dao = self._mapper.map(domain, self._dao)
        d = self._add_version_to_dao(dao)

        return d

    def _map_many_to_dict(self, domains: List[Domain]) -> List[dict]:
        dicts = self._mapper.map_many(
            domains, self._dao, after=self._add_version_to_dao
        )
        return dicts

    def _map_to_domain(self, record) -> Domain:
        dao = self._remap_record_to_lastest(record)
        result = self._mapper.map(dao, self._domain)
        return result

    def _map_many_to_domain(self, records: list) -> List[Domain]:
        daos = [self._remap_record_to_lastest(record) for record in records]
        results = self._mapper.map_many(daos, self._domain)
        return results

    def _remap_record_to_lastest(self, record):
        version = record.get("_version", None)

        if version is None or version == self._version:
            return self._dao(**record)

        return self._version_mappers[version][self._version](
            self._version_mappers, record
        )

    def _add_version_to_dao(self, dao: BaseModel) -> dict:
        d = dao.dict()

        if not self._version is None:
            d["_version"] = self._version

        return d

    async def _insert_many_raw(self, dicts: List[dict]) -> Awaitable:
        """
        Postgres specific bulk insert of daos
        """
        columns_name = [
            column_processor.name for column_processor in self._column_processors
        ]

        records = [
            [
                column_processor.processor(d[column_processor.name])
                for column_processor in self._column_processors
            ]
            for d in dicts
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

        filter_fields = self._mapper.map(query_filter, dict, query_filter.__class__)
        where_filter = self._build_and_column_filter(filter_fields)

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
        tuned_postgres_dialect = create_postgres_dialect()

        return [
            TableColumnProcessor(
                name=column.name,
                processor=column.type.bind_processor(tuned_postgres_dialect) or noop,
            )
            for column in self._table.c
            if not isinstance(column.server_default, FetchedValue)
        ]

    def _build_and_column_filter(self, fields: dict):
        condition = None

        for column_name, value in fields.items():
            if condition is None:
                condition = getattr(self._table.c, column_name) == value
            else:
                condition = and_(
                    condition, getattr(self._table.c, column_name) == value
                )

        return condition
