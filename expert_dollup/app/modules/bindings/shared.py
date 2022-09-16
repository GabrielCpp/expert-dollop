from starlette.requests import Request
import expert_dollup.app.mappings as app_mappings
import expert_dollup.infra.mappings as infra_mappings
from expert_dollup.shared.automapping import Mapper
from expert_dollup.shared.starlette_injection import *


def bind_mapper(builder: InjectorBuilder) -> None:
    def provide_mapper(injector: Injector) -> Mapper:
        mapper = Mapper(injector)
        mapper.add_all_mapper_from_module([app_mappings, infra_mappings])
        return mapper

    builder.add_singleton(Mapper, provide_mapper, injector=Injector)
    builder.add_singleton(Clock, DateTimeClock)
    builder.add_singleton(IdProvider, UniqueIdGenerator)


def bind_genenric_handlers(builder: InjectorBuilder) -> None:
    builder.add_factory(GraphqlPageHandler, GraphqlPageHandler, mapper=Mapper)
    builder.add_factory(HttpPageHandler, HttpPageHandler, mapper=Mapper)
    builder.add_factory(RequestHandler, RequestHandler, mapper=Mapper)
    builder.add_factory(
        PageHandlerProxy,
        PageHandlerProxy,
        http=HttpPageHandler,
        graphql=GraphqlPageHandler,
        request=Scoped[Request],
    )


def bind_shared_modules(builder: InjectorBuilder) -> None:
    bind_mapper(builder)
    bind_genenric_handlers(builder)
