from typing import Optional, List
from uuid import UUID
from expert_dollup.core.exceptions import InvalidObject
from expert_dollup.core.domains import *
from expert_dollup.shared.database_services import Page, Paginator, CollectionService
from expert_dollup.shared.starlette_injection import LoggerFactory
from expert_dollup.core.builders import ProjectDefinitionTreeBuilder
from expert_dollup.core.units import NodeValueValidation
from expert_dollup.core.repositories import ProjectDefinitionNodeRepository


class ProjectDefinitionNodeUseCase:
    def __init__(
        self,
        project_definition_node_paginator: Paginator[ProjectDefinitionNode],
        project_definition_service: CollectionService[ProjectDefinition],
        project_definition_node_repository: ProjectDefinitionNodeRepository,
        project_definition_tree_builder: ProjectDefinitionTreeBuilder,
        node_value_validation: NodeValueValidation,
        logger: LoggerFactory,
    ):
        self.project_definition_node_paginator = project_definition_node_paginator
        self.project_definition_service = project_definition_service
        self.project_definition_node_repository = project_definition_node_repository
        self.project_definition_tree_builder = project_definition_tree_builder
        self.node_value_validation = node_value_validation
        self.logger = logger.create(__name__)

    async def add(self, domain: ProjectDefinitionNode) -> ProjectDefinitionNode:
        await self._ensure_node_is_valid(domain)
        await self.project_definition_node_repository.insert(domain)
        return await self.find_by_id(domain.id)

    async def delete_by_id(self, id: UUID) -> None:
        await self.project_definition_node_repository.delete_child_of(id)
        await self.project_definition_node_repository.delete_by_id(id)

    async def update(self, domain: ProjectDefinitionNode) -> None:
        await self._ensure_node_is_valid(domain)
        await self.project_definition_node_repository.upserts([domain])
        return domain

    async def find_by_id(self, id: UUID) -> ProjectDefinitionNode:
        result = await self.project_definition_node_repository.find_by_id(id)
        return result

    async def find_project_nodes(
        self,
        project_definition_id: UUID,
        limit: int,
        next_page_token: Optional[str] = None,
    ) -> Page[ProjectDefinitionNode]:
        results = await self.project_definition_node_paginator.find_page(
            ProjectDefinitionNodeFilter(project_definition_id=project_definition_id),
            limit,
            next_page_token,
        )
        return results

    async def find_root_sections(
        self, project_definition_id: UUID
    ) -> List[ProjectDefinitionNode]:
        root_sections = (
            await self.project_definition_node_repository.find_root_sections(
                project_definition_id
            )
        )
        tree = self.project_definition_tree_builder.build(root_sections)
        return tree

    async def find_root_section_nodes(
        self, project_definition_id: UUID, root_section_id: UUID
    ) -> List[ProjectDefinitionNode]:
        nodes = await self.project_definition_node_repository.find_root_section_nodes(
            project_definition_id, root_section_id
        )
        tree = self.project_definition_tree_builder.build(nodes)
        return tree

    async def find_form_content(
        self, project_definition_id: UUID, form_id: UUID
    ) -> List[ProjectDefinitionNode]:
        form_definitions = (
            await self.project_definition_node_repository.find_form_content(
                project_definition_id, form_id
            )
        )
        tree = self.project_definition_tree_builder.build(form_definitions)
        return tree

    async def _ensure_node_is_valid(self, domain: ProjectDefinitionNode) -> None:
        has_project_def = await self.project_definition_service.has(
            domain.project_definition_id
        )

        if has_project_def is False:
            raise InvalidObject(
                "unexisting_parent_project",
                "Container must be attached to an existing parent project.",
            )

        if not await self.project_definition_node_repository.has_path(domain.path):
            raise InvalidObject("bad_tree_path", "Tree path is invalid.")

        # TODO: replace with propoer validation
        """
        self.node_value_validation.validate_value(
            domain, domain.field_details.default_value
        )
        """
