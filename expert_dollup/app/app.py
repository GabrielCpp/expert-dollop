from injector import Injector, Binder
from logging import Logger
from fastapi import FastAPI, APIRouter, Request
from ariadne.asgi import GraphQL
from dotenv import load_dotenv
from expert_dollup.infra.expert_dollup_db import ExpertDollupDatabase
import expert_dollup.app.controllers as api_routers
from .schemas import schema, GraphqlContext
from .modules import build_container
from .middlewares import (
    create_node_middleware,
    LoggerMiddleware,
    create_error_middleware,
    ExceptionHandlerDict,
)


def bind_request_modules(request: Request):
    def bind_request(binder: Binder) -> None:
        binder.bind(Request, to=request)

    return [bind_request]


def creat_app(container: Injector = None):
    load_dotenv()
    container = container or build_container()
    exception_handler = container.get(ExceptionHandlerDict)
    logger = container.get(Logger)

    app = FastAPI(debug=False)
    app.add_middleware(
        create_node_middleware(
            container,
            lambda parent, request: Injector(
                bind_request_modules(request), parent=parent
            ),
        )
    )
    app.add_middleware(LoggerMiddleware)
    app.add_middleware(create_error_middleware(exception_handler, logger))

    for router in api_routers.__dict__.values():
        if isinstance(router, APIRouter):
            app.include_router(router, prefix="/api")

    app.add_route(
        "/graphql",
        GraphQL(
            schema,
            debug=False,
            introspection=True,
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
