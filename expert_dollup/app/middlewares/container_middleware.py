from typing import Type, Dict, Callable
from fastapi import Depends
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from expert_dollup.shared.starlette_injection import *
from uuid import uuid4


def create_injector_middleware(injector: TypedInjection):
    class ContainerMiddleware(BaseHTTPMiddleware):
        async def dispatch(
            self,
            request: Request,
            call_next: RequestResponseEndpoint,
        ) -> Response:

            scoped_injector = injector.scoped(str(uuid4()))

            try:
                scoped_injector.bind_scoped_object(Request, request)
                request.state.injector = scoped_injector
                result = await call_next(request)
            finally:
                scoped_injector.destroy()

            return result

    return ContainerMiddleware
