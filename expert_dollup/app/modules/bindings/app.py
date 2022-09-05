import http.client as httplib
from typing import Dict, Any
from typing_extensions import TypeAlias
from starlette.responses import JSONResponse
from expert_dollup.app.middlewares import ExceptionHandlerDict
from expert_dollup.core.exceptions import *
from expert_dollup.app.handlers import *
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


def bind_error_handler(builder: InjectorBuilder) -> None:
    builder.add_object(ExceptionHandlerDict, exception_handlers)


def bind_auth_jwt(builder: InjectorBuilder) -> None:
    builder.add_factory(
        AuthService,
        AuthJWT,
        settings=AppSettings,
        user_service=Repository[User],
        ressource_service=Repository[Ressource],
        logger=Logger,
    )


def bind_custom_handlers(builder: InjectorBuilder) -> None:
    builder.add_factory(
        ImportRessourceHandler, ImportRessourceHandler, db_context=DatabaseContext
    )


def bind_app_modules(builder: InjectorBuilder) -> None:
    bind_error_handler(builder)
    bind_auth_jwt(builder)
    bind_custom_handlers(builder)
