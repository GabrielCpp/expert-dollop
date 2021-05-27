from typing import Type, Dict, Callable
from fastapi import Depends
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from injector import Injector


def create_node_middleware(
    global_node: Injector, build_request_node: Callable[[Injector], Injector]
):
    class ContainerMiddleware(BaseHTTPMiddleware):
        async def dispatch(
            self,
            request: Request,
            call_next: RequestResponseEndpoint,
        ) -> Response:

            request.state.global_node = global_node
            request.state.container = build_request_node(global_node, request)
            return await call_next(request)

    return ContainerMiddleware
