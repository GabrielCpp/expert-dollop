from injector import Binder, singleton
from predykt.shared.automapping import Mapper
import predykt.app.mappings as app_mappings
import predykt.infra.mappings as infra_mappings


def bind_mapper(binder: Binder) -> None:
    mapper = Mapper()
    mapper.add_all_mapper_from_module([app_mappings, infra_mappings])
    binder.bind(Mapper, to=mapper, scope=singleton)
