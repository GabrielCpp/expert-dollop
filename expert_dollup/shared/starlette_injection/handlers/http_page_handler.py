from typing import Optional, TypeVar, Generic, Type, List
from pydantic import BaseModel
from urllib.parse import unquote
from ...database_services import Paginator
from ...automapping import Mapper
from ..modeling import CamelModel

Domain = TypeVar("Domain")


def make_page_model(results_type: Type) -> CamelModel:
    Result = TypeVar("Result", bound=results_type)

    class PageDto(CamelModel):
        next_page_token: str
        limit: int
        has_next_page: bool
        results: List[Result]

    return PageDto


class HttpPageHandler(Generic[Domain]):
    def __init__(self, mapper: Mapper, paginator: Paginator[Domain]):
        self.mapper = mapper
        self.paginator = paginator

    async def handle(
        self,
        out_dto: Type[BaseModel],
        query_filter,
        limit: int,
        next_page_token: Optional[str] = None,
    ):
        page = await self.paginator.find_page(
            query_filter,
            limit,
            None if next_page_token is None else unquote(next_page_token),
        )

        return {
            "nextPageToken": page.next_page_token,
            "limit": page.limit,
            "hasNextPage": len(page.results) < limit,
            "results": self.mapper.map_many(page.results, out_dto),
        }
