from typing import List, Awaitable, Optional
from uuid import UUID, uuid4
from collections import defaultdict
from expert_dollup.core.domains import (
    ProjectDetails,
    ProjectNode,
    ProjectNodeFilter,
    ProjectDefinitionNodeFilter,
    BoundedNode,
)
from expert_dollup.infra.services import (
    ProjectNodeService,
    ProjectDefinitionNodeService,
)


class ProjectNodeSliceBuilder:
    def __init__(
        self,
        project_node_service: ProjectNodeService,
        project_definition_node_service: ProjectDefinitionNodeService,
    ):
        self.project_node_service = project_node_service
        self.project_definition_node_service = project_definition_node_service

    async def build_collection(
        self,
        project_details: ProjectDetails,
        collection_type_id: UUID,
        parent_node_id: Optional[UUID],
    ) -> Awaitable[List[BoundedNode]]:
        if parent_node_id is None:
            parent_node = ProjectNode(
                id=project_details.id,
                project_id=project_details.id,
                type_path=[],
                type_id=project_details.project_def_id,
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
                project_def_id=project_details.project_def_id, id=collection_type_id
            )
        )

        definition_nodes = await self.project_definition_node_service.find_children(
            project_details.project_def_id, root_def_node.subpath
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

        return bounded_nodes

    async def clone(self, project_id: UUID, node_id: UUID):
        parent_node = await self.project_node_service.find_one_by(
            ProjectNodeFilter(project_id=project_id, id=node_id)
        )

        children = await self.project_node_service.find_children(
            project_id, parent_node.subpath
        )

        id_mapping = defaultdict(uuid4, iter((item, item) for item in parent_node.path))

        nodes = [
            ProjectNode(
                id=id_mapping[node.id],
                project_id=node.project_id,
                type_id=node.type_id,
                type_name=node.type_name,
                type_path=node.type_path,
                path=[id_mapping[node_id] for node_id in node.path],
                value=node.value,
                label=node.label,
            )
            for node in [
                parent_node,
                *children,
            ]
        ]

        return nodes
