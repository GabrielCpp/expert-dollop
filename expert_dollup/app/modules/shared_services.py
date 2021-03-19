from injector import Binder, inject
from expert_dollup.shared.starlette_injection import factory_of, Constant
from expert_dollup.shared.automapping import Mapper
from expert_dollup.shared.handlers import RequestHandler, GraphqlPageHandler
from expert_dollup.infra.services import *
from expert_dollup.app.dtos import *


def bind_shared_services(binder: Binder) -> None:
    binder.bind(RequestHandler, inject(RequestHandler))

    graphql_handlers = [
        GraphqlPageHandler[DatasheetElementService, DatasheetElementDto]
    ]

    for graphql_handler in graphql_handlers:
        binder.bind(
            graphql_handler,
            factory_of(
                graphql_handler,
                mapper=Mapper,
                service=graphql_handler.__args__[0],
                out_dto=Constant(graphql_handler.__args__[1]),
            ),
        )
