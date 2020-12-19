from injector import Binder, inject
from predykt.core.usecases import ProjectDefinitonUseCase, ProjectDefinitonContainerUseCase


def bind_usecases(binder: Binder) -> None:
    binder.bind(ProjectDefinitonUseCase, inject(ProjectDefinitonUseCase))
    binder.bind(ProjectDefinitonContainerUseCase,
                inject(ProjectDefinitonContainerUseCase))
