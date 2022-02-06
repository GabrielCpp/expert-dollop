from typing import List
from uuid import UUID, uuid4
from collections import defaultdict, OrderedDict
from expert_dollup.core.utils.ressource_permissions import make_ressource
from expert_dollup.shared.starlette_injection import Clock
from expert_dollup.shared.database_services import CollectionService
from expert_dollup.core.domains import *


class TriggerHandler:
    def __init__(self, nodes_by_id: OrderedDict):
        self.nodes_by_id = nodes_by_id

    def run(self, bounded_node: BoundedNode):
        for trigger in bounded_node.definition.config.triggers:
            if trigger.action == TriggerAction.CHANGE_NAME:
                self._trigger_change_name(trigger, bounded_node)

    def _trigger_change_name(self, trigger: Trigger, bounded_node: BoundedNode):
        index = bounded_node.node.type_path.index(trigger.target_type_id)
        path = bounded_node.node.path[0 : index + 1]
        node = self.nodes_by_id[path[-1]]
        node.node.label = str(bounded_node.node.value)


class ProjectBuilder:
    def __init__(
        self,
        project_node_service: CollectionService[ProjectNode],
        project_node_meta_service: CollectionService[ProjectNodeMeta],
        project_definition_node_service: CollectionService[ProjectDefinitionNode],
        clock: Clock,
    ):
        self.project_definition_node_service = project_definition_node_service
        self.project_node_meta_service = project_node_meta_service
        self.project_node_service = project_node_service
        self.clock = clock

    async def build_new(
        self, project_details: ProjectDetails, user_id: UUID
    ) -> Project:
        node_definitions = await self.project_definition_node_service.find_by(
            ProjectDefinitionNodeFilter(project_def_id=project_details.project_def_id)
        )

        children_to_skip = set()
        nodes_by_id = OrderedDict()
        node_metas = []
        type_to_instance_id = defaultdict(uuid4)

        for node_definition in sorted(node_definitions, key=lambda d: d.path):
            node_meta = ProjectNodeMeta(
                project_id=project_details.id,
                type_id=node_definition.id,
                state=ProjectNodeMetaState(
                    is_visible=node_definition.config.meta.is_visible,
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
                type_name=node_definition.name,
                type_path=node_definition.path,
                path=[type_to_instance_id[def_id] for def_id in node_definition.path],
                value=node_definition.default_value,
            )

            nodes_by_id[node.id] = BoundedNode(node, node_definition)

        trigger_handler = TriggerHandler(nodes_by_id)

        for node in nodes_by_id.values():
            trigger_handler.run(node)

        nodes = [bounded_node.node for bounded_node in nodes_by_id.values()]

        return Project(
            details=project_details,
            nodes=nodes,
            metas=node_metas,
            ressource=make_ressource(ProjectDetails, project_details, user_id),
        )

    async def clone(self, project_details: ProjectDetails, user_id: UUID) -> Project:
        cloned_project = ProjectDetails(
            id=uuid4(),
            name=project_details.name,
            is_staged=False,
            project_def_id=project_details.project_def_id,
            datasheet_id=project_details.datasheet_id,
            creation_date_utc=self.clock.utcnow(),
        )

        ressource = make_ressource(ProjectDetails, cloned_project, user_id)
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
    ) -> List[ProjectNode]:
        original_nodes = await self.project_node_service.find_by(
            ProjectNodeFilter(project_id=project_id)
        )

        id_mapping = defaultdict(uuid4)
        cloned_nodes = [
            ProjectNode(
                id=id_mapping[node.id],
                project_id=cloned_project.id,
                type_id=node.type_id,
                type_name=node.type_name,
                type_path=node.type_path,
                path=[id_mapping[node_id] for node_id in node.path],
                value=node.value,
                label=node.label,
            )
            for node in original_nodes
        ]

        return cloned_nodes

    async def _clone_metas(
        self, project_id: UUID, cloned_project: ProjectDetails
    ) -> List[ProjectNodeMeta]:
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
