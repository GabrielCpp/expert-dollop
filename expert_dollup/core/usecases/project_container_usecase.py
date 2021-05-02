from typing import Awaitable, List, Optional
from uuid import UUID
from sqlalchemy import select, join, and_, desc, or_
from expert_dollup.core.units import NodeValueValidation
from expert_dollup.core.builders import ProjectNodeSliceBuilder, ProjectTreeBuilder
from expert_dollup.core.domains import (
    ProjectContainer,
    ProjectContainerTree,
    ProjectContainerFilter,
    ValueUnion,
)
from expert_dollup.infra.services import (
    ProjectService,
    ProjectContainerService,
    ProjectDefinitionNodeService,
    ProjectContainerMetaService,
)


class ProjectContainerUseCase:
    def __init__(
        self,
        project_service: ProjectService,
        project_container_service: ProjectContainerService,
        project_definition_node_service: ProjectDefinitionNodeService,
        node_value_validation: NodeValueValidation,
        project_node_slice_builder: ProjectNodeSliceBuilder,
        project_tree_builder: ProjectTreeBuilder,
        project_container_meta: ProjectContainerMetaService,
    ):
        self.project_service = project_service
        self.project_container_service = project_container_service
        self.project_definition_node_service = project_definition_node_service
        self.node_value_validation = node_value_validation
        self.project_node_slice_builder = project_node_slice_builder
        self.project_tree_builder = project_tree_builder
        self.project_container_meta = project_container_meta

    async def find_by_type(
        self, project_id: UUID, type_id: UUID
    ) -> Awaitable[List[ProjectContainer]]:
        results = await self.project_container_service.find_by(
            ProjectContainerFilter(project_id=project_id, type_id=type_id)
        )

        return results

    async def find_by_id(self, id: UUID) -> Awaitable[ProjectContainer]:
        node = await self.project_container_service.find_by_id(id)
        return node

    async def find_by_path(
        self, project_id: UUID, path: List[UUID], level: Optional[int] = None
    ) -> Awaitable[List[ProjectContainer]]:
        children = await self.project_container_service.find_children(project_id, path, level)
        return children

    async def find_subtree(self, project_id: UUID, path: List[UUID]):
        node = await self.project_container_service.find_by_id(path[-1])
        children = await self.project_container_service.find_children(project_id, path)
        return [node, *children]

    async def find_root_sections(
        self, project_id: UUID
    ) -> Awaitable[ProjectContainerTree]:
        roots = await self.project_container_service.find_root_sections(project_id)
        metas = await self.project_container_meta.find_root_sections(project_id)
        tree = self.project_tree_builder.build(roots, metas)
        return tree

    async def find_root_section_containers(
        self, project_id: UUID
    ) -> Awaitable[ProjectContainerTree]:
        roots = await self.project_container_service.find_root_section_containers(
            project_id
        )
        metas = await self.project_container_meta.find_root_section_containers(
            project_id
        )
        tree = self.project_tree_builder.build(roots, metas)
        return tree

    async def find_root_section_containers(
        self, project_id: UUID
    ) -> Awaitable[ProjectContainerTree]:
        roots = await self.project_container_service.find_form_content(project_id)
        metas = await self.project_container_meta.find_form_content(project_id)
        tree = self.project_tree_builder.build(roots, metas)
        return tree

    async def update_container_value(
        self, project_id: UUID, node_id: UUID, value: ValueUnion
    ):
        node = await self.project_container_service.find_one_by(
            ProjectContainerFilter(project_id=project_id, id=node_id)
        )

        definition_node = await self.project_definition_node_service.find_by_id(
            node.type_id
        )

        self.node_value_validation.validate_value(definition_node.config, value)

        await self.project_container_service.update(
            ProjectContainerFilter(value=value),
            ProjectContainerFilter(project_id=project_id, id=node_id),
        )

    async def add_collection(
        self,
        project_id: UUID,
        collection_type_id: UUID,
        parent_node_id: Optional[UUID],
    ) -> Awaitable[List[ProjectContainer]]:
        project_details = await self.project_service.find_by_id(project_id)
        nodes = await self.project_node_slice_builder.build_collection(
            project_details, collection_type_id, parent_node_id
        )
        await self.project_container_service.insert_many(nodes)
        return nodes

    async def clone_collection(
        self, project_id: UUID, node_id: UUID
    ) -> Awaitable[List[ProjectContainer]]:
        nodes = await self.project_node_slice_builder.clone(project_id, node_id)
        await self.project_container_service.insert_many(nodes)
        return nodes

    async def remove_collection(self, project_id: UUID, node_id: UUID) -> Awaitable:
        container = await self.project_container_service.find_one_by(
            ProjectContainerFilter(project_id=project_id, id=node_id)
        )
        await self.project_container_service.remove_collection(container)
        await self.project_container_service.delete_by_id(container.id)
