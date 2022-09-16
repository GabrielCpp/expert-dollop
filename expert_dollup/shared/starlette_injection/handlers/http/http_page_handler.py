from typing import Optional, TypeVar, Type, List
from pydantic import BaseModel
from urllib.parse import unquote
from ..interfaces import PageHandler
from ....database_services import Paginator, QueryFilter
from ....automapping import Mapper


Domain = TypeVar("Domain")


class HttpPageHandler(PageHandler):
    def __init__(self, mapper: Mapper):
        self._mapper = mapper
        self._paginator: Optional[Paginator] = None

    def use_paginator(self, paginator: Paginator[Domain]) -> PageHandler:
        self._paginator = paginator
        return self

    async def handle(
        self,
        out_dto: Type[BaseModel],
        query: QueryFilter,
        limit: int,
        next_page_token: Optional[str] = None,
    ):
        if self._paginator is None:
            raise Exception("No paginator set")

        page = await self._paginator.find_page(
            query,
            limit,
            None if next_page_token is None else unquote(next_page_token),
        )

        return {
            "nextPageToken": page.next_page_token,
            "limit": page.limit,
            "hasNextPage": len(page.results) < limit,
            "results": self._mapper.map_many(page.results, out_dto),
        }
