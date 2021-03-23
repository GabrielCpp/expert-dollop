import structlog
from typing import Awaitable, Optional
from uuid import UUID
from expert_dollup.core.exceptions import (
    RessourceNotFound,
    InvalidObject,
    FactorySeedMissing,
)
from expert_dollup.core.domains import (
    ProjectDefinitionNode,
    ProjectDefinition,
    ProjectDefinitionNodeFilter,
)
from expert_dollup.infra.services import (
    ProjectDefinitionNodeService,
    ProjectDefinitionService,
)
from expert_dollup.infra.validators import ProjectDefinitionValueTypeValidator
from expert_dollup.shared.database_services import Page

logger = structlog.get_logger(__name__)


class ProjectDefinitionNodeUseCase:
    def __init__(
        self,
        service: ProjectDefinitionNodeService,
        project_definition_service: ProjectDefinitionService,
        project_definition_value_type_validator: ProjectDefinitionValueTypeValidator,
    ):
        self.service = service
        self.project_definition_service = project_definition_service
        self.project_definition_value_type_validator = (
            project_definition_value_type_validator
        )

    async def add(
        self, domain: ProjectDefinitionNode
    ) -> Awaitable[ProjectDefinitionNode]:
        await self._ensure_container_is_valid(domain)
        await self.service.insert(domain)
        return await self.find_by_id(domain.id)

    async def remove_by_id(self, id: UUID) -> Awaitable:
        await self.service.delete_child_of(id)
        await self.service.delete_by_id(id)

    async def update(self, domain: ProjectDefinitionNode) -> Awaitable:
        await self._ensure_container_is_valid(domain)
        await self.service.update(domain)
        return await self.find_by_id(domain.id)

    async def find_by_id(self, id: UUID) -> Awaitable[ProjectDefinitionNode]:
        result = await self.service.find_by_id(id)
        return result

    async def find_project_containers(
        self, project_def_id: UUID, limit: int, next_page_token: Optional[str] = None
    ) -> Awaitable[Page[ProjectDefinitionNode]]:
        results = await self.service.find_by_paginated(
            ProjectDefinitionNodeFilter(project_def_id=project_def_id),
            limit,
            next_page_token,
        )
        return results

    async def find_viewable_layers(
        self,
        root_section_id: Optional[UUID],
        sub_root_section_id: Optional[UUID],
        form_id: Optional[UUID],
    ):
        pass

    async def _ensure_container_is_valid(self, domain: ProjectDefinitionNode):
        has_project_def = await self.project_definition_service.has(
            domain.project_def_id
        )

        if has_project_def is False:
            raise InvalidObject(
                "unexisting_parent_project",
                "Container must be attached to an existing parent project.",
            )

        if not await self.service.has_path(domain.path):
            raise InvalidObject("bad_tree_path", "Tree path is invalid.")

        try:
            await self.project_definition_value_type_validator.validate_config(
                domain.value_type, domain.config
            )

            await self.project_definition_value_type_validator.validate_value(
                domain.value_type, domain.config, domain.default_value
            )
        except FactorySeedMissing:
            ValidationError.for_field("value_type", "Value type not found")