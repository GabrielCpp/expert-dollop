from typing import Type, Dict, Callable
from fastapi import Depends
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from injector import Injector


def create_node_middleware(
    global_injector: Injector,
    build_request_node: Callable[[Injector, Request], Injector],
):
    class ContainerMiddleware(BaseHTTPMiddleware):
        async def dispatch(
            self,
            request: Request,
            call_next: RequestResponseEndpoint,
        ) -> Response:

            request.state.global_injector = global_injector
            request.state.container = build_request_node(global_injector, request)
            return await call_next(request)

    return ContainerMiddleware
