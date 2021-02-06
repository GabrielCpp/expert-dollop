from typing import Awaitable, List, Optional
from uuid import UUID
from expert_dollup.core.exceptions import RessourceNotFound
from expert_dollup.core.domains import (
    ProjectContainer,
    ProjectContainerTree,
    ProjectContainerFilter,
)
from expert_dollup.infra.services import (
    ProjectContainerService,
    ProjectDefinitionContainerService,
)
from expert_dollup.infra.validators import ProjectDefinitionValueTypeValidator
from expert_dollup.shared.database_services import Page


class ProjectContainerUseCase:
    def __init__(
        self,
        project_container_service: ProjectContainerService,
        project_definition_container_service: ProjectDefinitionContainerService,
        project_definition_value_type_validator: ProjectDefinitionValueTypeValidator,
    ):
        self.project_container_service = project_container_service
        self.project_definition_container_service = project_definition_container_service
        self.project_definition_value_type_validator = (
            project_definition_value_type_validator
        )

    async def find_by_id(self, id: UUID) -> Awaitable[ProjectContainer]:
        container = await self.project_container_service.find_by_id(id)
        return container

    async def find_by_path(
        self, project_id: UUID, path: List[UUID], level: Optional[int]
    ) -> Awaitable[ProjectContainerTree]:
        return await self.project_container_service.find_container_tree_by_path(
            project_id, path, level
        )

    async def remove(self, id: UUID) -> Awaitable:
        await self.project_container_service.remove(id)

    async def update_container_value(
        self, project_id: UUID, container_id: UUID, value: dict
    ):
        container = await self.project_container_service.find_one_by(
            ProjectContainerFilter(project_id=project_id, id=container_id)
        )

        container_definition = (
            await self.project_definition_container_service.find_by_id(
                container.type_id
            )
        )

        await self.project_definition_value_type_validator.validate_value(
            container_definition.value_type, container_definition.config, value
        )

        await self.project_container_service.update(
            ProjectContainerFilter(value=value),
            ProjectContainerFilter(project_id=project_id, id=container_id),
        )

    async def clone_collection(self, project_id: UUID, container_id: UUID):
        pass

    async def add_collection(self, project_id: UUID, container_type_id: UUID):
        pass
