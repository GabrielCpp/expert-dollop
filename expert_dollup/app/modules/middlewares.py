import http.client as httplib
from injector import Binder, singleton
from starlette.responses import JSONResponse
from expert_dollup.shared.problem import problem
from expert_dollup.app.middlewares import ExceptionHandlerDict
from expert_dollup.core.exceptions import *


exception_handlers = {
    RessourceNotFound: lambda e, r: JSONResponse(
        problem(title="Ressource not found", type="ressource-not-found"),
        status_code=httplib.NOT_FOUND,
    ),
    ValidationError: lambda e, r: JSONResponse(
        problem(title=e.message, type="validation-error", errors=e.errors),
        status_code=httplib.UNPROCESSABLE_ENTITY,
    ),
}


def bind_error_handler(binder: Binder) -> None:
    binder.bind(ExceptionHandlerDict, to=lambda: exception_handlers, scope=singleton)