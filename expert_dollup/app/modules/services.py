import inspect
import expert_dollup.infra.services as services
from injector import Binder, inject
from expert_dollup.shared.starlette_injection import factory_of
from expert_dollup.infra.expert_dollup_db import ExpertDollupDatabase


def bind_services(binder: Binder) -> None:
    for class_type in services.__dict__.values():
        if inspect.isclass(class_type):
            binder.bind(
                class_type, factory_of(class_type, database=ExpertDollupDatabase)
            )
