import expert_dollup.core.usecases as usecases
import expert_dollup.core.units as units
import expert_dollup.core.aggregates as aggregates
from inspect import isclass
from injector import Binder, inject
from itertools import chain
from expert_dollup.core.builders import *


def bind_core_classes(binder: Binder) -> None:
    binder.bind(RessourceBuilder, to=inject(RessourceBuilder))
    binder.bind(ProjectDefinitionTreeBuilder, to=inject(ProjectDefinitionTreeBuilder))

    for class_type in chain(
        usecases.__dict__.values(),
        units.__dict__.values(),
        aggregates.__dict__.values(),
    ):
        if isclass(class_type):
            binder.bind(class_type, inject(class_type))
