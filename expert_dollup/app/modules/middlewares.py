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

exception_handlers = {
    RessourceNotFound: lambda e, r: JSONResponse(
        problem(title="Ressource not found", type="ressource-not-found"),
        status_code=httplib.NOT_FOUND,
    ),
    RecordNotFound: lambda e, r: JSONResponse(
        problem(title="Ressource not found", type="ressource-not-found"),
        status_code=httplib.NOT_FOUND,
    ),
    ValidationError: lambda e, r: JSONResponse(
        problem(title=e.message, type="validation-error", errors=e.errors),
        status_code=httplib.UNPROCESSABLE_ENTITY,
    ),
    NoBearerAuthorizationHeader: lambda e, r: JSONResponse(
        problem(title="Unauthorized", type="unauthorized", errors=["Unauthorized"]),
        status_code=httplib.UNAUTHORIZED,
    ),
    InvalidBearerToken: lambda e, r: JSONResponse(
        problem(title="Unauthorized", type="unauthorized", errors=["Unauthorized"]),
        status_code=httplib.UNAUTHORIZED,
    ),
    PermissionMissing: lambda e, r: JSONResponse(
        problem(title="Forbidden", type="forbidden", errors=[e.props["reason"]]),
        status_code=httplib.FORBIDDEN,
    ),
}


def bind_error_handler(binder: Binder) -> None:
    binder.bind(ExceptionHandlerDict, to=lambda: exception_handlers, scope=singleton)
