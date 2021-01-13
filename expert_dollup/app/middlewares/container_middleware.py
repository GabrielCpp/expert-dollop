from typing import Type, Dict, Callable
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
from injector import Injector


def create_container_middleware(global_container: Injector, build_request_container: Callable[[Injector], Injector]):
    class ContainerMiddleware(BaseHTTPMiddleware):
        async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
        ) -> Response:

            request.state.global_container = global_container
            request.state.container = build_request_container(
                global_container)

            return await call_next(request)

    return ContainerMiddleware
