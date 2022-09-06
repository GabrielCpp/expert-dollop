from asyncio import gather
from typing import Optional, TypeVar
from uuid import UUID
from expert_dollup.shared.automapping import Mapper
from .page import Page
from .adapter_interfaces import (
    QueryBuilder,
    InternalRepository,
    Paginator,
    WhereFilter,
    PaginationDetails,
)


Domain = TypeVar("Domain")


class CollectionPaginator(Paginator[Domain]):
    def __init__(
        self,
        repository: InternalRepository[Domain],
        mapper: Mapper,
        pagination_details: PaginationDetails,
    ):
        self._default_page_encoder = pagination_details.default_page_encoder
        self._repository = repository
        self._mapper = mapper

    async def find_page(
        self,
        where_filter: Optional[WhereFilter],
        limit: int,
        next_page_token: Optional[str] = None,
    ) -> Page[Domain]:
        builder = (
            self._repository.get_builder()
            if where_filter is None
            else self._make_builder(where_filter)
        )
        self._default_page_encoder.extend_query(builder, limit, next_page_token)

        results, total_count = await gather(
            self._repository.find_by(builder), self._repository.count(where_filter)
        )
        print(total_count)
        new_next_page_token = self._default_page_encoder.default_token

        if len(results) > 0:
            last_result = results[-1]
            last_dao = self._repository.map_domain_to_dao(last_result)
            new_next_page_token = self._default_page_encoder.encode(last_dao)

        return Page(
            next_page_token=new_next_page_token,
            limit=limit,
            results=results,
            total_count=total_count,
        )

    def make_record_token(self, domain: Domain) -> str:
        dao = self._repository.map_domain_to_dao(domain)
        next_page_token = self._default_page_encoder.encode(dao)
        return next_page_token

    def _make_builder(self, where_filter: WhereFilter) -> QueryBuilder:
        if isinstance(where_filter, QueryBuilder):
            return where_filter.clone()

        columns_filter = self._mapper.map(where_filter, dict, where_filter.__class__)
        builder = self._repository.get_builder()

        for name, value in columns_filter.items():
            builder.where(name, "==", value)

        return builder
