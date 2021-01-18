from typing import Awaitable
from uuid import UUID
from expert_dollup.core.exceptions import (
    RessourceNotFound,
    InvalidObject,
    FactorySeedMissing,
)
from expert_dollup.core.domains import (
    ProjectDefinitionContainer,
    ProjectDefinition,
)
from expert_dollup.infra.services import (
    ProjectDefinitionContainerService,
    ProjectDefinitionService,
    ProjectDefinitionPluginService,
)
from expert_dollup.infra.factories import ValueTypeValidatorFactory
from expert_dollup.infra.validators import ProjectDefinitionConfigValidator


class IdentifiedRessourceUseCase:
    pass


class ProjectDefinitonContainerUseCase:
    def __init__(
        self,
        service: ProjectDefinitionContainerService,
        project_container_service: ProjectDefinitionService,
        value_type_validator_factory: ValueTypeValidatorFactory,
        project_definition_plugin_service: ProjectDefinitionPluginService,
        project_definition_config_validator: ProjectDefinitionConfigValidator,
    ):
        self.service = service
        self.project_container_service = project_container_service
        self.value_type_validator_factory = value_type_validator_factory
        self.project_definition_plugin_service = project_definition_plugin_service
        self.project_definition_config_validator = project_definition_config_validator

    async def add(
        self, domain: ProjectDefinitionContainer
    ) -> Awaitable[ProjectDefinitionContainer]:
        await self._ensure_container_is_valid(domain)
        await self.service.insert(domain)
        return await self.find_by_id(domain.id)

    async def remove_by_id(self, id: UUID) -> Awaitable:
        await self.service.delete_child_of(id)
        await self.service.delete_by_id(id)

    async def update(self, domain: ProjectDefinitionContainer) -> Awaitable:
        await self._ensure_container_is_valid(domain)
        await self.service.update(domain)
        return await self.find_by_id(domain.id)

    async def find_by_id(self, id: UUID) -> Awaitable[ProjectDefinitionContainer]:
        result = await self.service.find_by_id(id)

        if result is None:
            raise RessourceNotFound()

        return result

    async def _ensure_container_is_valid(self, domain: ProjectDefinitionContainer):
        project_def = await self.project_container_service.find_by_id(
            domain.project_def_id
        )

        if project_def is None:
            raise InvalidObject(
                "unexisting_parent_project",
                "Container must be attached to an existing parent project.",
            )

        if not await self.service.has_path(domain.path):
            raise InvalidObject("bad_tree_path", "Tree path is invalid.")

        await self._ensure_plugin_config_valid(project_def, domain)

        try:
            validate = self.value_type_validator_factory.create(domain.value_type)
            validate(domain.default_value)
        except FactorySeedMissing:
            ValidationError.for_field("value_type", "Value type not found")

    async def _ensure_plugin_config_valid(
        self, project_def: ProjectDefinition, domain: ProjectDefinitionContainer
    ) -> None:
        schema_by_name = (
            await self.project_definition_plugin_service.get_config_validation_schemas(
                project_def.plugins
            )
        )

        if len(schema_by_name) < len(project_def.plugins):
            raise RessourceNotFound("One or more plugin not found")

        self.project_definition_config_validator.validate(
            domain.custom_attributes, schema_by_name
        )
