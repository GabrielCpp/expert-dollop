import http.client as httplib
from injector import Binder, singleton
from starlette.responses import JSONResponse
from expert_dollup.shared.starlette_injection import problem
from expert_dollup.app.middlewares import ExceptionHandlerDict
from expert_dollup.core.exceptions import *
from expert_dollup.shared.database_services import RecordNotFound
from expert_dollup.app.jwt_auth import (
    NoBearerAuthorizationHeader,
    InvalidBearerToken,
    PermissionMissing,
)
from injector import Binder, inject
from expert_dollup.app.settings import load_app_settings
from expert_dollup.core.domains import User, Ressource
from expert_dollup.app.jwt_auth import AuthJWT
import expert_dollup.infra.services as services
from expert_dollup.shared.automapping import Mapper
from expert_dollup.shared.database_services import (
    CollectionService,
    Paginator,
    UserRessourcePaginator,
)
from expert_dollup.shared.starlette_injection import (
    RequestHandler,
    GraphqlPageHandler,
    HttpPageHandler,
    AuthService,
    factory_of,
    Constant,
    factory_of,
    get_classes,
    get_base,
    get_arg,
)


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
            user_service=CollectionService[User],
            ressource_service=CollectionService[Ressource],
        ),
    )


def bind_graphql_handlers(binder: Binder) -> None:
    service_by_domain = {
        get_arg(get_base(service_type)): service_type
        for service_type in get_classes(services)
    }

    for domain_type in service_by_domain.keys():
        binder.bind(
            GraphqlPageHandler[Paginator[domain_type]],
            factory_of(
                GraphqlPageHandler,
                mapper=Mapper,
                paginator=Paginator[domain_type],
            ),
        )

        binder.bind(
            GraphqlPageHandler[UserRessourcePaginator[domain_type]],
            factory_of(
                GraphqlPageHandler,
                mapper=Mapper,
                paginator=UserRessourcePaginator[domain_type],
            ),
        )


def bind_http_handlers(binder: Binder) -> None:
    service_by_domain = {
        get_arg(get_base(service_type)): service_type
        for service_type in get_classes(services)
    }

    for domain_type in service_by_domain.keys():
        binder.bind(
            HttpPageHandler[Paginator[domain_type]],
            factory_of(
                HttpPageHandler,
                mapper=Mapper,
                paginator=Paginator[domain_type],
            ),
        )


def bind_handlers(binder: Binder) -> None:
    binder.bind(RequestHandler, inject(RequestHandler))
