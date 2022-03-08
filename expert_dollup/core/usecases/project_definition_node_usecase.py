from typing import Awaitable, Optional, List
from uuid import UUID
from expert_dollup.core.exceptions import InvalidObject
from expert_dollup.core.domains import *
from expert_dollup.shared.database_services import Page, Paginator, CollectionService
from expert_dollup.shared.starlette_injection import LoggerFactory
from expert_dollup.core.builders import ProjectDefinitionTreeBuilder
from expert_dollup.core.units import NodeValueValidation


class ProjectDefinitionNodeUseCase:
    def __init__(
        self,
        service: CollectionService[ProjectDefinitionNode],
        project_definition_node_paginator: Paginator[ProjectDefinitionNode],
        project_definition_service: CollectionService[ProjectDefinition],
        project_definition_node_service: CollectionService[ProjectDefinitionNode],
        project_definition_tree_builder: ProjectDefinitionTreeBuilder,
        node_value_validation: NodeValueValidation,
        logger: LoggerFactory,
    ):
        self.service = service
        self.project_definition_node_paginator = project_definition_node_paginator
        self.project_definition_service = project_definition_service
        self.project_definition_node_service = project_definition_node_service
        self.project_definition_tree_builder = project_definition_tree_builder
        self.node_value_validation = node_value_validation
        self.logger = logger.create(__name__)

    async def add(
        self, domain: ProjectDefinitionNode
    ) -> Awaitable[ProjectDefinitionNode]:
        await self._ensure_node_is_valid(domain)
        await self.service.insert(domain)
        return await self.find_by_id(domain.id)

    async def delete_by_id(self, id: UUID) -> Awaitable:
        await self.service.delete_child_of(id)
        await self.service.delete_by_id(id)

    async def update(self, domain: ProjectDefinitionNode) -> Awaitable:
        await self._ensure_node_is_valid(domain)
        await self.service.update(domain)
        return await self.find_by_id(domain.id)

    async def find_by_id(self, id: UUID) -> Awaitable[ProjectDefinitionNode]:
        result = await self.service.find_by_id(id)
        return result

    async def find_project_nodes(
        self, project_def_id: UUID, limit: int, next_page_token: Optional[str] = None
    ) -> Awaitable[Page[ProjectDefinitionNode]]:
        results = await self.project_definition_node_paginator.find_page(
            ProjectDefinitionNodeFilter(project_def_id=project_def_id),
            limit,
            next_page_token,
        )
        return results

    async def find_root_sections(
        self, project_def_id: UUID
    ) -> Awaitable[List[ProjectDefinitionNode]]:
        root_sections = await self.project_definition_node_service.find_root_sections(
            project_def_id
        )
        tree = self.project_definition_tree_builder.build(root_sections)
        return tree

    async def find_root_section_nodes(
        self, project_def_id: UUID, root_section_id: UUID
    ) -> Awaitable[List[ProjectDefinitionNode]]:
        nodes = await self.project_definition_node_service.find_root_section_nodes(
            project_def_id, root_section_id
        )
        tree = self.project_definition_tree_builder.build(nodes)
        return tree

    async def find_form_content(
        self, project_def_id: UUID, form_id: UUID
    ) -> Awaitable[List[ProjectDefinitionNode]]:
        form_definitions = await self.project_definition_node_service.find_form_content(
            project_def_id, form_id
        )
        tree = self.project_definition_tree_builder.build(form_definitions)
        return tree

    async def _ensure_node_is_valid(self, domain: ProjectDefinitionNode):
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

        self.node_value_validation.validate_value(domain.config, domain.default_value)
