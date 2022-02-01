from injector import Injector
from logging import Logger
from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import JSONResponse
from expert_dollup.shared.fastapi_jwt_auth import AuthJWT
from expert_dollup.shared.fastapi_jwt_auth.exceptions import AuthJWTException
from ariadne.asgi import GraphQL
from dotenv import load_dotenv
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
    logger = container.get(Logger)

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
