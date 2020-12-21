from typing import Awaitable
from uuid import UUID
from predykt.core.exceptions import RessourceNotFound, InvalidObject, FactorySeedMissing
from predykt.core.domains import ProjectDefinitionContainer
from predykt.infra.services import ProjectDefinitionContainerService, ProjectDefinitionService
from predykt.infra.factories import ValueTypeValidatorFactory


class IdentifiedRessourceUseCase:
    pass


class ProjectDefinitonContainerUseCase:
    def __init__(
        self,
        service: ProjectDefinitionContainerService,
        project_container_service: ProjectDefinitionService,
        value_type_validator_factory: ValueTypeValidatorFactory
    ):
        self.service = service
        self.project_container_service = project_container_service
        self.value_type_validator_factory = value_type_validator_factory

    async def add(self, domain: ProjectDefinitionContainer) -> Awaitable:
        if not await self.project_container_service.has(domain.project_def_id):
            raise InvalidObject("unexisting_parent_project",
                                "Container must be attached to an existing parent project.")

        if not await self.service.has_path(domain.path):
            raise InvalidObject("bad_tree_path", "Tree path is invalid.")

        try:
            validate = self.value_type_validator_factory.create(
                domain.value_type)
            validate(domain.default_value)
        except FactorySeedMissing:
            ValidationError.for_field("value_type", "Value type not found")

        await self.service.insert(domain)

    async def remove_by_id(self, id: UUID) -> Awaitable:
        await self.service.delete_by_id(id)

    async def update(self, domain: ProjectDefinitionContainer) -> Awaitable:
        await self.service.update(domain)

    async def find_by_id(self, id: UUID) -> Awaitable[ProjectDefinitionContainer]:
        result = await self.service.find_by_id(id)

        if result is None:
            raise RessourceNotFound()

        return result
