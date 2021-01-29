from injector import Binder, inject
from expert_dollup.core.builders import *


def bind_builders(binder: Binder) -> None:
    inject(RessourceBuilder)
    binder.bind(RessourceBuilder, to=RessourceBuilder)
