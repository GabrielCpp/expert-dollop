from typing import List, Optional
from uuid import UUID
from expert_dollup.core.domains.bounded_node import BoundedNode
from expert_dollup.core.units import NodeValueValidation, NodeEventDispatcher
from expert_dollup.core.builders import ProjectNodeSliceBuilder, ProjectTreeBuilder
from expert_dollup.core.domains import *
from expert_dollup.shared.database_services import CollectionService


class ProjectNodeUseCase:
    def __init__(
        self,
        project_service: CollectionService[ProjectDetails],
        project_node_service: CollectionService[ProjectNode],
        node_event_dispatcher: NodeEventDispatcher,
        node_value_validation: NodeValueValidation,
        project_node_slice_builder: ProjectNodeSliceBuilder,
        project_tree_builder: ProjectTreeBuilder,
        project_node_meta: CollectionService[ProjectNodeMeta],
    ):
        self.project_service = project_service
        self.project_node_service = project_node_service
        self.node_event_dispatcher = node_event_dispatcher
        self.node_value_validation = node_value_validation
        self.project_node_slice_builder = project_node_slice_builder
        self.project_tree_builder = project_tree_builder
        self.project_node_meta = project_node_meta

    async def find_by_type(self, project_id: UUID, type_id: UUID) -> List[ProjectNode]:
        results = await self.project_node_service.find_by(
            ProjectNodeFilter(project_id=project_id, type_id=type_id)
        )

        return results

    async def find_by_id(self, id: UUID) -> ProjectNode:
        node = await self.project_node_service.find_by_id(id)
        return node

    async def find_by_path(
        self, project_id: UUID, path: List[UUID], level: Optional[int] = None
    ) -> List[ProjectNode]:
        children = await self.project_node_service.find_children(
            project_id, path, level
        )
        return children

    async def find_subtree(self, project_id: UUID, path: List[UUID]):
        node = await self.project_node_service.find_by_id(path[-1])
        children = await self.project_node_service.find_children(project_id, path)
        return [node, *children]

    async def find_root_sections(self, project_id: UUID) -> ProjectNodeTree:
        roots = await self.project_node_service.find_root_sections(project_id)
        metas = await self.project_node_meta.find_root_sections(project_id)
        tree = self.project_tree_builder.build(roots, metas)
        return tree

    async def find_root_section_nodes(
        self, project_id: UUID, root_section_id: UUID
    ) -> ProjectNodeTree:
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
    ) -> ProjectNodeTree:
        form = await self.project_node_service.find_by_id(form_id)
        roots = await self.project_node_service.find_form_content(project_id, form_id)
        metas = await self.project_node_meta.find_form_content(project_id, form.type_id)
        await self.node_event_dispatcher.update_value_inplace(roots, metas)
        tree = self.project_tree_builder.build(roots, metas)
        return tree

    async def update_node_value(
        self, project_id: UUID, node_id: UUID, value: PrimitiveWithNoneUnion
    ) -> ProjectNode:
        return await self.node_event_dispatcher.update_node_value(
            project_id, node_id, value
        )

    async def update_nodes_value(
        self, project_id: UUID, updates: List[FieldUpdate]
    ) -> List[ProjectNode]:
        results = await self.node_event_dispatcher.update_nodes_value(
            project_id, updates
        )
        return results

    async def imports(self, nodes: List[ProjectNode]):
        if len(nodes) == 0:
            return

        await self.project_node_service.insert_many(nodes)
        project_id = nodes[0].project_id
        definitions = await self.project_node_meta.find_project_defs(project_id)
        definitions_by_id = {definition.id: definition for definition in definitions}

        for node in nodes:
            definition = definitions_by_id[node.type_id]
            bounded_node = BoundedNode(node=node, definition=definition)
            await self.node_event_dispatcher.execute_node_trigger(bounded_node)

    async def add_collection(
        self,
        project_id: UUID,
        collection_type_id: UUID,
        parent_node_id: Optional[UUID],
    ) -> List[ProjectNode]:
        project_details = await self.project_service.find_by_id(project_id)
        bounded_node_slice = await self.project_node_slice_builder.build_collection(
            project_details, collection_type_id, parent_node_id
        )
        nodes = [bounded_node.node for bounded_node in bounded_node_slice.bounded_nodes]
        await self.project_node_service.insert_many(nodes)

        for bounded_node in bounded_node_slice.bounded_nodes:
            await self.node_event_dispatcher.execute_node_trigger(bounded_node)

        return nodes

    async def clone_collection(
        self, project_id: UUID, node_id: UUID
    ) -> List[ProjectNode]:
        bounded_node_slice = await self.project_node_slice_builder.clone(
            project_id, node_id
        )
        nodes = [bounded_node.node for bounded_node in bounded_node_slice.bounded_nodes]
        await self.project_node_service.insert_many(nodes)

        for bounded_node in bounded_node_slice.bounded_nodes:
            await self.node_event_dispatcher.execute_node_trigger(bounded_node)

        return nodes

    async def remove_collection(self, project_id: UUID, node_id: UUID) -> ProjectNode:
        node = await self.project_node_service.find_one_by(
            ProjectNodeFilter(project_id=project_id, id=node_id)
        )
        await self.project_node_service.remove_collection(node)
        await self.project_node_service.delete_by_id(node.id)
        return node
