from injector import Binder, inject
from itertools import chain
import expert_dollup.core.usecases as usecases
import expert_dollup.core.units as units
import inspect


def bind_core_classes(binder: Binder) -> None:
    for class_type in chain(usecases.__dict__.values(), units.__dict__.values()):
        if inspect.isclass(class_type):
            binder.bind(class_type, inject(class_type))
