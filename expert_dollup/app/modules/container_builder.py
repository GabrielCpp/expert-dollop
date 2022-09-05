from typing import Callable, List
from starlette.requests import Request
from expert_dollup.shared.starlette_injection import (
    Injector,
    TypedInjection,
    InjectorBuilder,
)
from expert_dollup.app.settings import load_app_settings, AppSettings
from .bindings import *


def build_container(
    overrides: List[Callable[[InjectorBuilder], None]] = []
) -> TypedInjection:
    builder = InjectorBuilder()
    builder.add_container_self()
    builder.add_scoped(Request)
    builder.add_object(AppSettings, load_app_settings())

    bind_logger(builder)
    bind_shared_modules(builder)
    bind_io_modules(builder)
    bind_app_modules(builder)
    bind_core_modules(builder)

    for override in overrides:
        override(builder)

    return builder.build()
