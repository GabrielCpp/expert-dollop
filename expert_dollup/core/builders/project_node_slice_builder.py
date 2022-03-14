from typing import Optional
from uuid import UUID, uuid4
from collections import defaultdict
from expert_dollup.core.domains import *
from expert_dollup.shared.database_services import CollectionService
from .unit_instance_builder import UnitInstanceBuilder


class ProjectNodeSliceBuilder:
    def __init__(
        self,
        project_node_service: CollectionService[ProjectNode],
        project_definition_node_service: CollectionService[ProjectDefinitionNode],
        unit_instance_builder: UnitInstanceBuilder,
    ):
        self.project_node_service = project_node_service
        self.project_definition_node_service = project_definition_node_service
        self.unit_instance_builder = unit_instance_builder

    async def build_collection(
        self,
        project_details: ProjectDetails,
        collection_type_id: UUID,
        parent_node_id: Optional[UUID],
    ) -> BoundedNodeSlice:
        if parent_node_id is None:
            parent_node = ProjectNode(
                id=project_details.id,
                project_id=project_details.id,
                type_path=[],
                type_id=project_details.project_definition_id,
                type_name="",
                path=[],
                value=None,
            )
        else:
            parent_node = await self.project_node_service.find_one_by(
                ProjectNodeFilter(project_id=project_details.id, id=parent_node_id)
            )

        root_def_node = await self.project_definition_node_service.find_one_by(
            ProjectDefinitionNodeFilter(
                project_definition_id=project_details.project_definition_id,
                id=collection_type_id,
            )
        )

        definition_nodes = await self.project_definition_node_service.find_children(
            project_details.project_definition_id, root_def_node.subpath
        )

        type_to_instance_id = defaultdict(
            uuid4,
            zip(
                parent_node.type_subpath,
                parent_node.subpath,
            ),
        )

        bounded_nodes = [
            BoundedNode(
                node=ProjectNode(
                    id=type_to_instance_id[definition_node.id],
                    project_id=project_details.id,
                    type_id=definition_node.id,
                    type_name=definition_node.name,
                    type_path=definition_node.path,
                    path=[
                        type_to_instance_id[def_id] for def_id in definition_node.path
                    ],
                    value=definition_node.default_value,
                ),
                definition=definition_node,
            )
            for definition_node in [
                root_def_node,
                *definition_nodes,
            ]
        ]

        unit_instances = await self.unit_instance_builder.build(
            project_details.project_definition_id,
            [bounded_node.node for bounded_node in bounded_nodes],
        )

        return BoundedNodeSlice(
            bounded_nodes=bounded_nodes, unit_instances=unit_instances
        )

    async def clone(self, project_id: UUID, node_id: UUID):
        parent_node = await self.project_node_service.find_one_by(
            ProjectNodeFilter(project_id=project_id, id=node_id)
        )

        children = await self.project_node_service.find_children(
            project_id, parent_node.subpath
        )

        root_def_node = await self.project_definition_node_service.find_one_by(
            ProjectDefinitionNodeFilter(id=parent_node.type_id)
        )

        definition_nodes = await self.project_definition_node_service.find_children(
            root_def_node.project_definition_id, root_def_node.subpath
        )

        id_mapping = defaultdict(uuid4, iter((item, item) for item in parent_node.path))

        bounded_nodes = [
            BoundedNode(
                node=ProjectNode(
                    id=id_mapping[node.id],
                    project_id=node.project_id,
                    type_id=node.type_id,
                    type_name=node.type_name,
                    type_path=node.type_path,
                    path=[id_mapping[node_id] for node_id in node.path],
                    value=node.value,
                    label=node.label,
                ),
                definition=definition,
            )
            for definition, node in zip(
                [root_def_node, *definition_nodes],
                [
                    parent_node,
                    *children,
                ],
            )
        ]

        unit_instances = await self.unit_instance_builder.build(
            root_def_node.project_definition_id,
            [bounded_node.node for bounded_node in bounded_nodes],
        )

        return BoundedNodeSlice(
            bounded_nodes=bounded_nodes, unit_instances=unit_instances
        )
