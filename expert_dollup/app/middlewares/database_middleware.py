from typing import Type
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp


def create_database_transaction_middleware(database_type: Type):
    class DatabaseTransactionMiddleware(BaseHTTPMiddleware):
        async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
        ) -> Response:
            container = request.state.container
            database = container.get(database_type)

            async with database.transaction():
                response = await call_next(request)
                return response

    return DatabaseTransactionMiddleware
