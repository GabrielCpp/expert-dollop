from injector import Binder, inject
from expert_dollup.core.usecases import (
    ProjectDefinitonUseCase,
    ProjectDefinitonContainerUseCase,
    TranslationUseCase,
    ProjectUseCase,
)


def bind_usecases(binder: Binder) -> None:
    usecases = [
        ProjectDefinitonUseCase,
        ProjectDefinitonContainerUseCase,
        TranslationUseCase,
        ProjectUseCase,
    ]

    for usecase_type in usecases:
        binder.bind(usecase_type, inject(usecase_type))
