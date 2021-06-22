from typing import Optional, TypeVar, Generic, Type, List
from urllib.parse import unquote
from ..modeling import CamelModel
from ..automapping import Mapper

Service = TypeVar("Service")
OutDto = TypeVar("OutDto")

def make_page_model(results_type: Type) -> CamelModel:
    Result = TypeVar('Result', bound=results_type)

    class PageDto(CamelModel):
        next_page_token: str
        limit: int
        has_next_page: bool
        results: List[Result]

    return PageDto


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
