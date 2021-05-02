from typing import List, Awaitable, Optional
from uuid import UUID, uuid4
from collections import defaultdict
from expert_dollup.core.domains import (
    ProjectDetails,
    ProjectContainer,
    ProjectContainerFilter,
    ProjectDefinitionNodeFilter,
)
from expert_dollup.infra.services import (
    ProjectContainerService,
    ProjectDefinitionNodeService,
)


class ProjectNodeSliceBuilder:
    def __init__(
        self,
        project_container_service: ProjectContainerService,
        project_definition_node_service: ProjectDefinitionNodeService,
    ):
        self.project_container_service = project_container_service
        self.project_definition_node_service = project_definition_node_service

    async def build_collection(
        self,
        project_details: ProjectDetails,
        collection_type_id: UUID,
        parent_node_id: Optional[UUID],
    ):
        if parent_node_id is None:
            parent_node = ProjectContainer(
                id=project_details.id,
                project_id=project_details.id,
                type_path=[],
                type_id=project_details.project_def_id,
                path=[],
                value=None,
            )
        else:
            parent_node = await self.project_container_service.find_one_by(
                ProjectContainerFilter(project_id=project_id, id=parent_node_id)
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

        nodes = [
            ProjectContainer(
                id=type_to_instance_id[definition_node.id],
                project_id=project_details.id,
                type_id=definition_node.id,
                type_path=definition_node.path,
                path=[type_to_instance_id[def_id] for def_id in definition_node.path],
                value=definition_node.default_value,
            )
            for definition_node in [
                root_def_node,
                *definition_nodes,
            ]
        ]

        return nodes

    async def clone(self, project_id: UUID, node_id: UUID):
        parent_node = await self.project_container_service.find_one_by(
            ProjectContainerFilter(project_id=project_id, id=node_id)
        )

        children = await self.project_container_service.find_children(
            project_id, parent_node.subpath
        )

        id_mapping = defaultdict(uuid4, iter((item, item) for item in parent_node.path))

        nodes = [
            ProjectContainer(
                id=id_mapping[node.id],
                project_id=node.project_id,
                type_id=node.type_id,
                type_path=node.type_path,
                path=[id_mapping[node_id] for node_id in node.path],
                value=node.value,
            )
            for node in [
                parent_node,
                *children,
            ]
        ]

        return nodes
