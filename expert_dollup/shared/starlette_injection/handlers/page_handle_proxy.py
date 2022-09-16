from typing import List, Callable, TypeVar, Type, Optional
from pydantic import BaseModel
from starlette.requests import Request
from .interfaces import PageHandler
from .graphql import GraphqlPageHandler
from .http import HttpPageHandler
from ..injection import Scoped
from ...database_services import Paginator, QueryFilter

Domain = TypeVar("Domain")


class PageHandlerProxy(PageHandler):
    def __init__(
        self,
        request: Scoped[Request],
        graphql: GraphqlPageHandler,
        http: HttpPageHandler,
    ):
        self._request = request
        self._graphql_handler = graphql
        self._http_handler = http

    def use_paginator(self, paginator: Paginator[Domain]) -> PageHandler:
        self._graphql_handler.use_paginator(paginator)
        self._http_handler.use_paginator(paginator)
        return self

    async def handle(
        self,
        out_dto: Type[BaseModel],
        query: QueryFilter,
        limit: int,
        next_page_token: Optional[str] = None,
    ):
        if self._request.value.url.path.endswith("/graphql"):
            return await self._graphql_handler.handle(
                out_dto, query, limit, next_page_token
            )

        return await self._http_handler.handle(out_dto, query, limit, next_page_token)
