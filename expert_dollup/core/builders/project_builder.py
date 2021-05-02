from typing import List, Awaitable
from uuid import UUID, uuid4
from collections import defaultdict
from expert_dollup.core.builders import RessourceBuilder
from expert_dollup.core.domains import (
    Project,
    ProjectDetails,
    ProjectNode,
    ProjectNodeMeta,
    ProjectDefinitionNodeFilter,
    ProjectNodeFilter,
    ProjectNodeMetaFilter,
    ProjectNodeMetaState,
)
from expert_dollup.infra.services import (
    ProjectNodeService,
    ProjectNodeMetaService,
    ProjectDefinitionNodeService,
)


class ProjectBuilder:
    def __init__(
        self,
        project_node_service: ProjectNodeService,
        project_node_meta_service: ProjectNodeMetaService,
        project_definition_node_service: ProjectDefinitionNodeService,
        ressource_builder: RessourceBuilder,
    ):
        self.project_definition_node_service = project_definition_node_service
        self.project_node_meta_service = project_node_meta_service
        self.ressource_builder = ressource_builder
        self.project_node_service = project_node_service

    async def build_new(self, project_details: ProjectDetails) -> Awaitable[Project]:
        node_definitions = await self.project_definition_node_service.find_by(
            ProjectDefinitionNodeFilter(project_def_id=project_details.project_def_id)
        )

        children_to_skip = set()
        nodes = []
        node_metas = []
        type_to_instance_id = defaultdict(uuid4)

        for node_definition in sorted(node_definitions, key=lambda d: d.path):
            node_meta = ProjectNodeMeta(
                project_id=project_details.id,
                type_id=node_definition.id,
                state=ProjectNodeMetaState(
                    is_visible=node_definition.instanciate_by_default,
                    selected_child=None,
                ),
                definition=node_definition,
            )

            node_metas.append(node_meta)

            if any(item in children_to_skip for item in node_definition.path):
                continue

            if node_definition.instanciate_by_default == False:
                children_to_skip.add(node_definition.id)
                continue

            node_id = type_to_instance_id[node_definition.id]
            node = ProjectNode(
                id=node_id,
                project_id=project_details.id,
                type_id=node_definition.id,
                type_path=node_definition.path,
                path=[type_to_instance_id[def_id] for def_id in node_definition.path],
                value=node_definition.default_value,
            )

            nodes.append(node)

        return Project(
            details=project_details,
            nodes=nodes,
            metas=node_metas,
            ressource=self.ressource_builder.build(
                project_details.id, project_details.id, "project"
            ),
        )

    async def clone(self, project_details: ProjectDetails) -> Awaitable[Project]:
        cloned_project = ProjectDetails(
            id=uuid4(),
            name=project_details.name,
            is_staged=False,
            project_def_id=project_details.project_def_id,
            datasheet_id=project_details.datasheet_id,
        )

        ressource = self.ressource_builder.build(
            cloned_project.id, cloned_project.id, "project"
        )

        cloned_nodes = await self._clone_project_nodes(
            project_details.id, cloned_project
        )

        cloned_metas = await self._clone_metas(project_details.id, cloned_project)

        return Project(
            details=cloned_project,
            nodes=cloned_nodes,
            metas=cloned_metas,
            ressource=ressource,
        )

    async def _clone_project_nodes(
        self, project_id: UUID, cloned_project: ProjectDetails
    ) -> Awaitable[List[ProjectNode]]:
        original_nodes = await self.project_node_service.find_by(
            ProjectNodeFilter(project_id=project_id)
        )

        id_mapping = defaultdict(uuid4)
        cloned_nodes = [
            ProjectNode(
                id=id_mapping[node.id],
                project_id=cloned_project.id,
                type_id=node.type_id,
                type_path=node.type_path,
                path=[id_mapping[node_id] for node_id in node.path],
                value=node.value,
            )
            for node in original_nodes
        ]

        return cloned_nodes

    async def _clone_metas(
        self, project_id: UUID, cloned_project: ProjectDetails
    ) -> Awaitable[List[ProjectNodeMeta]]:
        node_metas = await self.project_node_meta_service.find_by(
            ProjectNodeMetaFilter(project_id=project_id)
        )

        node_type_metas = [
            ProjectNodeMeta(
                project_id=cloned_project.id,
                type_id=meta.type_id,
                state=meta.state,
                definition=meta.definition,
            )
            for meta in node_metas
        ]

        return node_type_metas
