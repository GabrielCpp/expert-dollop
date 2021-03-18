import structlog
from datetime import datetime, timezone
from injector import Injector
from typing import Optional
from fastapi import FastAPI, APIRouter
from ariadne.asgi import GraphQL
from dotenv import load_dotenv
from structlog import configure
from structlog.contextvars import merge_contextvars
from expert_dollup.infra.expert_dollup_db import ExpertDollupDatabase
import expert_dollup.app.controllers as api_routers
from .schemas import schema, GraphqlContext
from .modules import build_container
from .middlewares import (
    create_database_transaction_middleware,
    create_container_middleware,
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


def creat_app(container: Injector = None):
    container = container or build_container()
    exception_handler = container.get(ExceptionHandlerDict)

    app = FastAPI()
    app.add_middleware(create_database_transaction_middleware(ExpertDollupDatabase))
    app.add_middleware(
        create_container_middleware(container, lambda parent: Injector(parent=parent))
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
            debug=True,
            introspection=True,
            context_value=GraphqlContext(container=container),
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
