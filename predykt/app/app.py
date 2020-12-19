import structlog
import datetime
from injector import Injector
from typing import Optional
from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from structlog import configure
from structlog.contextvars import merge_contextvars
from predykt.infra.predykt_db import PredyktDatabase
import predykt.app.controllers.project as api_routers
from .modules import build_container
from .middlewares import create_database_transaction_middleware, create_container_middleware, LoggerMiddleware, create_error_middleware, ExceptionHandlerDict


def add_timestamp(_, __, event_dict):
    event_dict["timestamp"] = str(datetime.datetime.utcnow().isoformat())
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
    app.add_middleware(
        create_database_transaction_middleware(PredyktDatabase))
    app.add_middleware(create_container_middleware(
        container, lambda parent: Injector(parent=parent)))
    app.add_middleware(LoggerMiddleware)
    app.add_middleware(create_error_middleware(exception_handler))

    for router in api_routers.__dict__.values():
        if isinstance(router, APIRouter):
            app.include_router(
                router,
                prefix="/api"
            )

    database = container.get(PredyktDatabase)

    @app.on_event("startup")
    async def startup():
        await database.connect()

    @app.on_event("shutdown")
    async def shutdown():
        await database.disconnect()

    return app
