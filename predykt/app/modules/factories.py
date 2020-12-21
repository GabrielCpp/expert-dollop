from injector import Binder, inject
from predykt.infra.factories import ValueTypeValidatorFactory


def bind_factories(binder: Binder) -> None:
    binder.bind(ValueTypeValidatorFactory, inject(ValueTypeValidatorFactory))
