import structlog
from typing import Type, Dict, Callable, TypeVar
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp


ExceptionHandler = Dict[Type, Callable[[Exception, Request], Response]]
InteralErrorHandler = Callable[[], Response]
ExceptionHandlerDict = TypeVar("ExceptionHandlerDict")

logger = structlog.get_logger(__name__)


def create_default_internal_error_response() -> Response:
    return Response(
        '{ "type": "internal-error", "title": "Internal Error", "detail": "Something went wrong." }',
        media_type="application/json",
        status_code=500,
    )


def create_error_middleware(
    handlers: ExceptionHandler,
    internal_error: InteralErrorHandler = create_default_internal_error_response,
):
    class ErrorMiddleware(BaseHTTPMiddleware):
        async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
        ) -> Response:
            try:
                return await call_next(request)
            except Exception as e:
                exception_type = type(e)

                if exception_type not in handlers:
                    logger.exception(
                        f"Unexpected error arrive out of controller ({exception_type})",
                        message=str(e),
                    )
                    return internal_error()

                handler = handlers[exception_type]
                return self._handle_error(handler, e, request)

        def _handle_error(
            self, handler: ExceptionHandler, e: Exception, request: Request
        ) -> Response:
            try:
                return handler(e, request)
            except Exception as e:
                logger.exception(
                    "Unexpected error arrive out of handler", message=str(e)
                )
                return internal_error()

    return ErrorMiddleware
