from injector import Injector, InstanceProvider, singleton
from .bindings import *


def build_container(root_binded=[]) -> Injector:
    injector = Injector(root_binded)

    injector.binder.bind(Injector, to=InstanceProvider(injector), scope=singleton)
    bind_logger(injector.binder)
    bind_shared_modules(injector.binder)
    bind_core_modules(injector.binder)
    bind_app_modules(injector.binder)
    bind_io_modules(injector.binder)

    return injector
