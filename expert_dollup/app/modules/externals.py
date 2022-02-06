import expert_dollup.app.mappings as app_mappings
import expert_dollup.infra.mappings as infra_mappings
from injector import Binder, singleton, Injector, Provider
from expert_dollup.shared.automapping import Mapper
from expert_dollup.shared.starlette_injection import (
    Clock,
    DateTimeClock,
    IdProvider,
    UniqueIdGenerator,
)


def bind_mapper(binder: Binder) -> None:
    class MapperProvider(Provider):
        def __init__(self):
            self.mapper = None

        def get(self, injector: Injector) -> Mapper:
            if self.mapper is None:
                mapper = Mapper(injector)
                mapper.add_all_mapper_from_module([app_mappings, infra_mappings])
                self.mapper = mapper

            return self.mapper

    binder.bind(Mapper, to=MapperProvider(), scope=singleton)
    binder.bind(Clock, to=DateTimeClock(), scope=singleton)
    binder.bind(IdProvider, to=UniqueIdGenerator(), scope=singleton)
