from injector import Binder, singleton
from expert_dollup.shared.automapping import Mapper
import expert_dollup.app.mappings as app_mappings
import expert_dollup.infra.mappings as infra_mappings


def bind_mapper(binder: Binder) -> None:
    mapper = Mapper()
    mapper.add_all_mapper_from_module([app_mappings, infra_mappings])
    binder.bind(Mapper, to=mapper, scope=singleton)
