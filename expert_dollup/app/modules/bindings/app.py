import http.client as httplib
from injector import Binder, singleton, inject
from typing import Dict, Any
from typing_extensions import TypeAlias
from starlette.responses import JSONResponse
from expert_dollup.app.middlewares import ExceptionHandlerDict
from expert_dollup.core.exceptions import *
from expert_dollup.app.settings import load_app_settings
import expert_dollup.app.handlers as handlers
from expert_dollup.app.jwt_auth import *
from expert_dollup.core.domains import User, Ressource
from expert_dollup.shared.automapping import Mapper
from expert_dollup.shared.database_services import *
from expert_dollup.shared.starlette_injection import *
from ..definitions import auth_metadatas, expert_dollup_metadatas, paginations

exception_handlers = {
    RessourceNotFound: lambda e: JSONResponse(
        problem(title="Ressource not found", type="ressource-not-found"),
        status_code=httplib.NOT_FOUND,
    ),
    RecordNotFound: lambda e: JSONResponse(
        problem(title="Ressource not found", type="ressource-not-found"),
        status_code=httplib.NOT_FOUND,
    ),
    ValidationError: lambda e: JSONResponse(
        problem(title=e.message, type="validation-error", errors=e.errors),
        status_code=httplib.UNPROCESSABLE_ENTITY,
    ),
    NoBearerAuthorizationHeader: lambda e: JSONResponse(
        problem(title="Unauthorized", type="unauthorized", errors=["Unauthorized"]),
        status_code=httplib.UNAUTHORIZED,
    ),
    InvalidBearerToken: lambda e: JSONResponse(
        problem(title="Unauthorized", type="unauthorized", errors=["Unauthorized"]),
        status_code=httplib.UNAUTHORIZED,
    ),
    PermissionMissing: lambda e: JSONResponse(
        problem(title="Ressource not found", type="ressource-not-found"),
        status_code=httplib.NOT_FOUND,
    ),
}


def bind_error_handler(binder: Binder) -> None:
    binder.bind(ExceptionHandlerDict, to=lambda: exception_handlers, scope=singleton)


def bind_auth_jwt(binder: Binder) -> None:
    binder.bind(
        AuthService,
        to=factory_of(
            AuthJWT,
            settings=Constant(load_app_settings()),
            user_service=Repository[User],
            ressource_service=Repository[Ressource],
        ),
    )


def bind_graphql_handlers(binder: Binder) -> None:
    for pagination in paginations:
        binder.bind(
            GraphqlPageHandler[Paginator[pagination.for_domain]],
            factory_of(
                GraphqlPageHandler,
                mapper=Mapper,
                paginator=Paginator[pagination.for_domain],
            ),
        )

        binder.bind(
            GraphqlPageHandler[UserRessourcePaginator[pagination.for_domain]],
            factory_of(
                GraphqlPageHandler,
                mapper=Mapper,
                paginator=UserRessourcePaginator[pagination.for_domain],
            ),
        )


def bind_http_handlers(binder: Binder) -> None:
    for pagination in paginations:
        binder.bind(
            HttpPageHandler[Paginator[pagination.for_domain]],
            factory_of(
                HttpPageHandler,
                mapper=Mapper,
                paginator=Paginator[pagination.for_domain],
            ),
        )


def bind_handlers(binder: Binder) -> None:
    binder.bind(RequestHandler, inject(RequestHandler))
    for handler in get_classes(handlers):
        binder.bind(handler, inject(handler))


def bind_app_modules(binder: Binder) -> None:
    bind_error_handler(binder)
    bind_auth_jwt(binder)
    bind_graphql_handlers(binder)
    bind_http_handlers(binder)
    bind_handlers(binder)
