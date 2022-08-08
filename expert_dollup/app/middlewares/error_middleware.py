from typing import Type, Dict, Callable, TypeVar
from logging import Logger
from graphql import GraphQLError
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from ariadne import format_error

ExceptionHandler = Dict[Type, Callable[[Exception], Response]]
InteralErrorHandler = Callable[[], Response]
ExceptionHandlerDict = TypeVar("ExceptionHandlerDict")


def create_default_internal_error_response() -> Response:
    return Response(
        '{ "type": "internal-error", "title": "Internal Error", "detail": "Something went wrong." }',
        media_type="application/json",
        status_code=500,
    )


def create_error_formatter(
    handlers: ExceptionHandler,
    logger: Logger,
    internal_error: InteralErrorHandler = create_default_internal_error_response,
):
    def error_formatter(e: Exception) -> Response:
        exception_type = type(e)
        handler = handlers.get(exception_type)

        if handler is None:
            logger.exception(
                f"Unexpected error arrive out of controller ({exception_type})",
                extra=dict(message=str(e)),
            )
            return internal_error()

        try:
            return handler(e)
        except Exception as e:
            logger.exception(
                "Unexpected error arrive out of handler", extra=dict(message=str(e))
            )
            return internal_error()

    return error_formatter


def create_graphql_error_formatter(
    handlers: ExceptionHandler,
    logger: Logger,
    internal_error: InteralErrorHandler = create_default_internal_error_response,
):
    format_request_error = create_error_formatter(handlers, logger, internal_error)

    def my_format_error(error: GraphQLError, debug: bool = False) -> dict:
        if debug:
            # If debug is enabled, reuse Ariadne's formatting logic (not required)
            return format_error(error, debug)

        # Create formatted error data
        formatted = error.formatted
        # Replace original error message with custom one
        formatted["message"] = format_request_error(error.original_error).body.decode(
            "utf8"
        )

        return formatted

    return my_format_error


def create_error_middleware(
    handlers: ExceptionHandler,
    logger: Logger,
    internal_error: InteralErrorHandler = create_default_internal_error_response,
):
    format_error = create_error_formatter(handlers, logger, internal_error)

    class ErrorMiddleware(BaseHTTPMiddleware):
        async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
        ) -> Response:
            try:
                return await call_next(request)
            except Exception as e:
                return format_error(e)

    return ErrorMiddleware
