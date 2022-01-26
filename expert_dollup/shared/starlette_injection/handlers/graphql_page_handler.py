from typing import Optional, TypeVar, Generic, Type
from pydantic import BaseModel
from ...database_services import Paginator
from ...automapping import Mapper


Domain = TypeVar("Domain")
OutDto = TypeVar("OutDto")


class GraphqlPageHandler(Generic[Domain]):
    def __init__(self, mapper: Mapper, paginator: Paginator[Domain]):
        self.mapper = mapper
        self.paginator = paginator

    async def find_all(
        self, out_dto: Type[OutDto], limit: int, next_page_token: Optional[str] = None
    ):
        page = await self.paginator.find_page(None, limit, next_page_token)

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

    async def handle(
        self,
        out_dto: Type[OutDto],
        query_filter,
        limit: int,
        next_page_token: Optional[str] = None,
    ):
        page = await self.paginator.find_page(query_filter, limit, next_page_token)

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
