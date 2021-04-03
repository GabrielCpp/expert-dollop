from typing import Type, Optional, TypeVar, Generic
from dataclasses import dataclass
from urllib.parse import unquote
from ..automapping import Mapper

Service = TypeVar("Service")
OutDto = TypeVar("OutDto")


class HttpPageHandler(Generic[Service, OutDto]):
    def __init__(self, mapper: Mapper, service: Service, out_dto: OutDto):
        self.mapper = mapper
        self.service = service
        self.out_dto = out_dto

    async def handle(
        self, query_filter, limit: int, next_page_token: Optional[str] = None
    ):
        page = await self.service.find_by_paginated(
            query_filter,
            limit,
            None if next_page_token is None else unquote(next_page_token),
        )

        return {
            "nextPageToken": page.next_page_token,
            "limit": page.limit,
            "hasNextPage": len(page.results) < limit,
            "results": self.mapper.map_many(page.results, self.out_dto),
        }
