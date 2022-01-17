from injector import Binder, inject
from expert_dollup.shared.database_services.adapter_interfaces import Paginator
from expert_dollup.shared.starlette_injection import (
    factory_of,
    get_classes,
    get_base,
    get_arg,
)
from expert_dollup.shared.automapping import Mapper
from expert_dollup.shared.starlette_injection import (
    RequestHandler,
    GraphqlPageHandler,
    HttpPageHandler,
)
from expert_dollup.infra.services import *
from expert_dollup.app.dtos import *
import expert_dollup.infra.services as services


def bind_graphql_handlers(binder: Binder) -> None:
    service_by_domain = {
        get_arg(get_base(service_type)): service_type
        for service_type in get_classes(services)
    }

    for domain_type in service_by_domain.keys():
        binder.bind(
            GraphqlPageHandler[domain_type],
            factory_of(
                GraphqlPageHandler[domain_type],
                mapper=Mapper,
                paginator=Paginator[domain_type],
            ),
        )


def bind_http_handlers(binder: Binder) -> None:
    service_by_domain = {
        get_arg(get_base(service_type)): service_type
        for service_type in get_classes(services)
    }

    for domain_type in service_by_domain.keys():
        binder.bind(
            HttpPageHandler[domain_type],
            factory_of(
                HttpPageHandler[domain_type],
                mapper=Mapper,
                paginator=Paginator[domain_type],
            ),
        )


def bind_handlers(binder: Binder) -> None:
    binder.bind(RequestHandler, inject(RequestHandler))
