from typing import Type, Optional, TypeVar, Generic
from dataclasses import dataclass
from ..automapping import Mapper
from ..database_services import Page

Service = TypeVar("Service")
OutDto = TypeVar("OutDto")


class GraphqlPageHandler(Generic[Service, OutDto]):
    def __init__(self, mapper: Mapper, service: Service, out_dto: OutDto):
        self.mapper = mapper
        self.service = service
        self.out_dto = out_dto

    async def handle(
        self, query_filter, limit: int, next_page_token: Optional[str] = None
    ):
        page = await self.service.find_by_paginated(
            query_filter, limit, next_page_token
        )

        return {
            "edges": [
                {
                    "node": self.mapper.map(result, self.out_dto),
                    "cursor": self.service.make_record_token(result),
                }
                for result in page.results
            ],
            "pageInfo": {
                "hasNextPage": len(page.results) < limit,
                "endCursor": page.next_page_token,
            },
        }