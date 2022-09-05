from os import getenv
from typing import Optional
from logging import Logger
from fastapi import FastAPI, APIRouter, Request
from ariadne.asgi import GraphQL
from dotenv import load_dotenv
from expert_dollup.shared.starlette_injection import TypedInjection
from expert_dollup.infra.expert_dollup_db import ExpertDollupDatabase
import expert_dollup.app.controllers as api_routers
from .schemas import schema, GraphqlContext
from .modules import build_container
from .middlewares import (
    create_injector_middleware,
    LoggerMiddleware,
    create_error_middleware,
    create_graphql_error_formatter,
    ExceptionHandlerDict,
)


def is_debug_enabled():
    return getenv("DEBUG") == "true"


def creat_app(injector: Optional[TypedInjection] = None):
    load_dotenv()
    injector = injector or build_container()
    exception_handler = injector.get(ExceptionHandlerDict)
    logger = injector.get(Logger)
    debug = is_debug_enabled()

    logger.info("Injection container creation is done")

    app = FastAPI(debug=debug)
    app.add_middleware(create_injector_middleware(injector))
    app.add_middleware(LoggerMiddleware)
    app.add_middleware(create_error_middleware(exception_handler, logger))

    for router in api_routers.__dict__.values():
        if isinstance(router, APIRouter):
            app.include_router(router, prefix="/api")

    app.add_route(
        "/graphql",
        GraphQL(
            schema,
            debug=debug,
            introspection=debug,
            error_formatter=create_graphql_error_formatter(exception_handler, logger),
            context_value=lambda request: GraphqlContext(
                injector=request.state.injector, request=request
            ),
        ),
        methods=["GET", "POST"],
    )

    database = injector.get(ExpertDollupDatabase)

    @app.get("/health")
    def check_health():
        return "ok"

    @app.on_event("startup")
    async def startup():
        if not database.is_connected:
            await database.connect()

    @app.on_event("shutdown")
    async def shutdown():
        if database.is_connected:
            await database.disconnect()

    return app
