from typing import Awaitable, List, Optional
from uuid import UUID
from sqlalchemy import select, join, and_, desc, or_
from expert_dollup.core.units import NodeValueValidation
from expert_dollup.core.builders import ProjectNodeSliceBuilder, ProjectTreeBuilder
from expert_dollup.core.domains import (
    ProjectNode,
    ProjectNodeTree,
    ProjectNodeFilter,
    ValueUnion,
)
from expert_dollup.infra.services import (
    ProjectService,
    ProjectNodeService,
    ProjectDefinitionNodeService,
    ProjectNodeMetaService,
)


class ProjectNodeUseCase:
    def __init__(
        self,
        project_service: ProjectService,
        project_node_service: ProjectNodeService,
        project_definition_node_service: ProjectDefinitionNodeService,
        node_value_validation: NodeValueValidation,
        project_node_slice_builder: ProjectNodeSliceBuilder,
        project_tree_builder: ProjectTreeBuilder,
        project_node_meta: ProjectNodeMetaService,
    ):
        self.project_service = project_service
        self.project_node_service = project_node_service
        self.project_definition_node_service = project_definition_node_service
        self.node_value_validation = node_value_validation
        self.project_node_slice_builder = project_node_slice_builder
        self.project_tree_builder = project_tree_builder
        self.project_node_meta = project_node_meta

    async def find_by_type(
        self, project_id: UUID, type_id: UUID
    ) -> Awaitable[List[ProjectNode]]:
        results = await self.project_node_service.find_by(
            ProjectNodeFilter(project_id=project_id, type_id=type_id)
        )

        return results

    async def find_by_id(self, id: UUID) -> Awaitable[ProjectNode]:
        node = await self.project_node_service.find_by_id(id)
        return node

    async def find_by_path(
        self, project_id: UUID, path: List[UUID], level: Optional[int] = None
    ) -> Awaitable[List[ProjectNode]]:
        children = await self.project_node_service.find_children(
            project_id, path, level
        )
        return children

    async def find_subtree(self, project_id: UUID, path: List[UUID]):
        node = await self.project_node_service.find_by_id(path[-1])
        children = await self.project_node_service.find_children(project_id, path)
        return [node, *children]

    async def find_root_sections(self, project_id: UUID) -> Awaitable[ProjectNodeTree]:
        roots = await self.project_node_service.find_root_sections(project_id)
        metas = await self.project_node_meta.find_root_sections(project_id)
        tree = self.project_tree_builder.build(roots, metas)
        return tree

    async def find_root_section_nodes(
        self, project_id: UUID, root_section_id: UUID
    ) -> Awaitable[ProjectNodeTree]:
        root_section = await self.project_node_service.find_by_id(root_section_id)
        roots = await self.project_node_service.find_root_section_nodes(
            project_id, root_section_id
        )
        metas = await self.project_node_meta.find_root_section_nodes(
            project_id, root_section.type_id
        )
        tree = self.project_tree_builder.build(roots, metas)
        return tree

    async def find_form_content(
        self, project_id: UUID, form_id: UUID
    ) -> Awaitable[ProjectNodeTree]:
        form = await self.project_node_service.find_by_id(form_id)
        roots = await self.project_node_service.find_form_content(project_id, form_id)
        metas = await self.project_node_meta.find_form_content(project_id, form.type_id)
        tree = self.project_tree_builder.build(roots, metas)
        return tree

    async def update_node_value(
        self, project_id: UUID, node_id: UUID, value: ValueUnion
    ) -> Awaitable[ProjectNode]:
        node = await self.project_node_service.find_one_by(
            ProjectNodeFilter(project_id=project_id, id=node_id)
        )

        definition_node = await self.project_definition_node_service.find_by_id(
            node.type_id
        )

        self.node_value_validation.validate_value(definition_node.config, value)

        await self.project_node_service.update(
            ProjectNodeFilter(value=value),
            ProjectNodeFilter(project_id=project_id, id=node_id),
        )

        return await self.project_node_service.find_by_id(node_id)

    async def add_collection(
        self,
        project_id: UUID,
        collection_type_id: UUID,
        parent_node_id: Optional[UUID],
    ) -> Awaitable[List[ProjectNode]]:
        project_details = await self.project_service.find_by_id(project_id)
        nodes = await self.project_node_slice_builder.build_collection(
            project_details, collection_type_id, parent_node_id
        )
        await self.project_node_service.insert_many(nodes)
        return nodes

    async def clone_collection(
        self, project_id: UUID, node_id: UUID
    ) -> Awaitable[List[ProjectNode]]:
        nodes = await self.project_node_slice_builder.clone(project_id, node_id)
        await self.project_node_service.insert_many(nodes)
        return nodes

    async def remove_collection(self, project_id: UUID, node_id: UUID) -> Awaitable:
        container = await self.project_node_service.find_one_by(
            ProjectNodeFilter(project_id=project_id, id=node_id)
        )
        await self.project_node_service.remove_collection(container)
        await self.project_node_service.delete_by_id(container.id)