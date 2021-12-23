from typing import Optional, TypeVar, Generic
from ...automapping import Mapper


Service = TypeVar("Service")
OutDto = TypeVar("OutDto")


class GraphqlPageHandler(Generic[Service, OutDto]):
    def __init__(self, mapper: Mapper, service: Service, out_dto: OutDto):
        self.mapper = mapper
        self.service = service
        self.out_dto = out_dto

    async def find_all(self, limit: int, next_page_token: Optional[str] = None):
        page = await self.service.find_all_paginated(limit, next_page_token)

        return {
            "edges": [
                {
                    "node": self.mapper.map(result, self.out_dto),
                    "cursor": self.service.make_record_token(result),
                }
                for result in page.results
            ],
            "page_info": {
                "has_next_page": len(page.results) == limit,
                "end_cursor": page.next_page_token,
                "total_count": self.service.count(),
            },
        }

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
            "page_info": {
                "has_next_page": len(page.results) == limit,
                "end_cursor": page.next_page_token,
                "total_count": self.service.count(query_filter),
            },
        }