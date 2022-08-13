from asyncio import gather
from typing import Optional, TypeVar
from uuid import UUID
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
