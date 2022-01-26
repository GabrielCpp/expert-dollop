import base64
from asyncio import gather
from typing import Optional, Any, TypeVar
from uuid import UUID
from pydantic import BaseModel
from expert_dollup.shared.automapping import Mapper
from .adapter_interfaces import QueryBuilder, CollectionService, Paginator, WhereFilter
from .page import Page

Domain = TypeVar("Domain")


class CollectionPaginator(Paginator[Domain]):
    def __init__(self, service: CollectionService[Domain], mapper: Mapper):
        meta = self.__class__.Meta
        self._default_page_encoder = meta.default_page_encoder
        self._service = service
        self._mapper = mapper

    async def find_page(
        self,
        where_filter: Optional[WhereFilter],
        limit: int,
        next_page_token: Optional[str] = None,
    ) -> Page[Domain]:
        builder = (
            self._service.get_builder()
            if where_filter is None
            else self._make_builder(where_filter)
        )
        self._default_page_encoder.extend_query(builder, limit, next_page_token)
        results, total_count = await gather(
            self._service.find_by(builder), self._service.count(where_filter)
        )

        new_next_page_token = self._default_page_encoder.default_token

        if len(results) > 0:
            last_result = results[-1]
            last_dao = self._mapper.map(last_result, self._service.dao)
            new_next_page_token = self._default_page_encoder.encode(last_dao)

        return Page(
            next_page_token=new_next_page_token,
            limit=limit,
            results=results,
            total_count=total_count,
        )

    def make_record_token(self, domain: Domain) -> str:
        dao = self._mapper.map(domain, self._service.dao)
        next_page_token = self._default_page_encoder.encode(dao)
        return next_page_token

    def _make_builder(self, where_filter: WhereFilter) -> QueryBuilder:
        if isinstance(where_filter, QueryBuilder):
            return where_filter.clone()

        columns_filter = self._mapper.map(where_filter, dict, where_filter.__class__)
        builder = self._service.get_builder()

        for name, value in columns_filter.items():
            builder.where(name, "==", value)

        return builder


class FieldTokenEncoder:
    def __init__(
        self,
        id_field_name: str,
        build_id_field: callable = UUID,
        extract_field_id: callable = str,
        default_id: str = UUID("00000000-0000-0000-0000-000000000000"),
    ):
        self.id_field_name = id_field_name
        self._build_id_field = build_id_field
        self._extract_field_id = extract_field_id
        self.default_token = self._encode(default_id)

    def extend_query(
        self, builder: WhereFilter, limit: int, next_page_token: Optional[str]
    ) -> QueryBuilder:
        id_column = self.id_field_name

        if not next_page_token is None:
            from_id = self.decode(next_page_token)
            builder.where(id_column, "<", from_id)

        return builder.orderby((id_column, "desc")).limit(limit)

    def encode(self, dao: BaseModel):
        dao_id = getattr(dao, self.id_field_name)
        return self._encode(dao_id)

    def _encode(self, dao_id: str):
        id_str = self._extract_field_id(dao_id)
        token = base64.urlsafe_b64encode(id_str.encode("utf8"))
        return token.decode("utf8")

    def decode(self, cursor: str) -> Any:
        id_field_str = base64.urlsafe_b64decode(cursor.encode("utf8"))
        id_field = self._build_id_field(id_field_str.decode("utf8"))
        return id_field
