from typing import Optional, TypeVar, Type
from pydantic import BaseModel
from ..interfaces import PageHandler
from ....database_services import Paginator, QueryFilter
from ....automapping import Mapper

Domain = TypeVar("Domain")


class GraphqlPageHandler(PageHandler):
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

        page = await self.paginator.find_page(query, limit, next_page_token)

        return {
            "edges": [
                {
                    "node": self._mapper.map(result, out_dto),
                    "cursor": self._paginator.make_record_token(result),
                }
                for result in page.results
            ],
            "page_info": {
                "has_next_page": len(page.results) == limit,
                "end_cursor": page.next_page_token,
                "total_count": page.total_count,
            },
        }
