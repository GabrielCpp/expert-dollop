import expert_dollup.core.usecases as usecases
import expert_dollup.core.units as units
import expert_dollup.core.builders as builders
from inspect import isclass
from injector import Binder, inject
from itertools import chain


def bind_core_classes(binder: Binder) -> None:
    for class_type in chain(
        usecases.__dict__.values(),
        units.__dict__.values(),
        builders.__dict__.values(),
    ):
        if isclass(class_type):
            binder.bind(class_type, inject(class_type))
