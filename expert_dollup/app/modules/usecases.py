from injector import Binder, inject
from expert_dollup.core.usecases import *


def bind_usecases(binder: Binder) -> None:
    usecases = [
        ProjectDefinitonUseCase,
        ProjectDefinitonContainerUseCase,
        TranslationUseCase,
        ProjectUseCase,
        ProjectContainerUseCase,
    ]

    for usecase_type in usecases:
        binder.bind(usecase_type, inject(usecase_type))
