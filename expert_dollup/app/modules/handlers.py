from injector import Binder, inject
from expert_dollup.shared.starlette_injection import factory_of, Constant
from expert_dollup.shared.automapping import Mapper
from expert_dollup.shared.handlers import (
    RequestHandler,
    GraphqlPageHandler,
    HttpPageHandler,
)
from expert_dollup.infra.services import *
from expert_dollup.app.dtos import *


def bind_graphql_handlers(binder: Binder) -> None:
    handlers = [
        GraphqlPageHandler[DatasheetElementService, DatasheetElementDto],
        GraphqlPageHandler[ProjectDefinitionService, ProjectDefinitionDto],
        GraphqlPageHandler[ProjectService, ProjectDetailsDto],
        GraphqlPageHandler[DatasheetDefinitionService, DatasheetDefinitionDto],
        GraphqlPageHandler[
            DatasheetDefinitionElementService, DatasheetDefinitionElementDto
        ],
        GraphqlPageHandler[FormulaService, FormulaExpressionDto],
        GraphqlPageHandler[DatasheetService, DatasheetDto],
    ]

    for handler in handlers:
        binder.bind(
            handler,
            factory_of(
                handler,
                mapper=Mapper,
                service=handler.__args__[0],
                out_dto=Constant(handler.__args__[1]),
            ),
        )


def bind_http_handlers(binder: Binder) -> None:
    handlers = [
        HttpPageHandler[DatasheetElementService, DatasheetElementDto],
        HttpPageHandler[TranslationService, TranslationDto],
    ]

    for handler in handlers:
        binder.bind(
            handler,
            factory_of(
                handler,
                mapper=Mapper,
                service=handler.__args__[0],
                out_dto=Constant(handler.__args__[1]),
            ),
        )


def bind_handlers(binder: Binder) -> None:
    binder.bind(RequestHandler, inject(RequestHandler))
