from injector import Binder, inject
from predykt.infra.validators import ProjectDefinitionConfigValidator


def bind_validators(binder: Binder) -> None:
    binder.bind(ProjectDefinitionConfigValidator,
                ProjectDefinitionConfigValidator)
