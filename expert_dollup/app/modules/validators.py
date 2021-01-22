from injector import Binder, inject
from expert_dollup.shared.starlette_injection import factory_of
from expert_dollup.infra.validators import ProjectDefinitionValueTypeValidator
from expert_dollup.infra.services import ProjectDefinitionValueTypeService


def bind_validators(binder: Binder) -> None:
    binder.bind(
        ProjectDefinitionValueTypeValidator,
        factory_of(
            ProjectDefinitionValueTypeValidator,
            value_type_service=ProjectDefinitionValueTypeService,
        ),
    )
