from typing import Optional, TypeVar, Generic, Type
from injector import Injector
from pydantic import BaseModel
from ...database_services import Paginator, QueryFilter
from ...automapping import Mapper

PaginatorService = TypeVar("PaginatorService")
Domain = TypeVar("Domain")
OutDto = TypeVar("OutDto")


class GraphqlPageHandler(Generic[PaginatorService]):
    def __init__(self, mapper: Mapper, paginator: Paginator[Domain]):
        self.mapper = mapper
        self.paginator = paginator

    async def handle(
        self,
        out_dto: Type[OutDto],
        query: QueryFilter,
        limit: int,
        next_page_token: Optional[str] = None,
    ):
        page = await self.paginator.find_page(query, limit, next_page_token)

        return {
            "edges": [
                {
                    "node": self.mapper.map(result, out_dto),
                    "cursor": self.paginator.make_record_token(result),
                }
                for result in page.results
            ],
            "page_info": {
                "has_next_page": len(page.results) == limit,
                "end_cursor": page.next_page_token,
                "total_count": page.total_count,
            },
        }
