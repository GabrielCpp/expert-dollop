import structlog
from datetime import datetime, timezone
from injector import Injector
from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import JSONResponse
from expert_dollup.shared.fastapi_jwt_auth import AuthJWT
from expert_dollup.shared.fastapi_jwt_auth.exceptions import AuthJWTException
from ariadne.asgi import GraphQL
from dotenv import load_dotenv
from structlog import configure
from structlog.contextvars import merge_contextvars
from expert_dollup.infra.expert_dollup_db import ExpertDollupDatabase
import expert_dollup.app.controllers as api_routers
from .settings import load_app_settings
from .schemas import schema, GraphqlContext
from .modules import build_container
from .middlewares import (
    create_node_middleware,
    LoggerMiddleware,
    create_error_middleware,
    ExceptionHandlerDict,
)


def add_timestamp(_, __, event_dict):
    event_dict["timestamp"] = str(datetime.now(timezone.utc).isoformat())
    return event_dict


configure(
    processors=[
        merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        add_timestamp,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.dev.ConsoleRenderer(),
        structlog.processors.JSONRenderer(indent=1, sort_keys=True),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

load_dotenv()


def auth_jwt_singleton():
    AuthJWT


from injector import Binder, singleton


def bind_request_modules(request: Request):
    def bind_request(binder: Binder) -> None:
        binder.bind(Request, to=request, scope=singleton)

    def bind_error_handler(binder: Binder) -> None:
        binder.bind(AuthJWT, to=AuthJWT(request), scope=singleton)

    return [bind_request, bind_error_handler]


def creat_app(container: Injector = None):
    container = container or build_container()
    exception_handler = container.get(ExceptionHandlerDict)

    app = FastAPI(debug=False)

    @AuthJWT.load_config
    def get_config():
        return load_app_settings()

    @app.exception_handler(AuthJWTException)
    def authjwt_exception_handler(request: Request, exc: AuthJWTException):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.message}
        )

    app.add_middleware(
        create_node_middleware(
            container,
            lambda parent, request: Injector(
                bind_request_modules(request), parent=parent
            ),
        )
    )
    app.add_middleware(LoggerMiddleware)
    app.add_middleware(create_error_middleware(exception_handler))

    for router in api_routers.__dict__.values():
        if isinstance(router, APIRouter):
            app.include_router(router, prefix="/api")

    app.add_route(
        "/graphql",
        GraphQL(
            schema,
            debug=False,
            introspection=False,
            context_value=lambda request: GraphqlContext(
                container=request.state.container, request=request
            ),
        ),
        methods=["GET", "POST"],
    )

    database = container.get(ExpertDollupDatabase)

    @app.on_event("startup")
    async def startup():
        if not database.is_connected:
            await database.connect()

    @app.on_event("shutdown")
    async def shutdown():
        if database.is_connected:
            await database.disconnect()

    return app
