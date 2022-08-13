from typing import List
from uuid import UUID
from expert_dollup.shared.database_services import CollectionService
from expert_dollup.core.builders import *
from expert_dollup.core.domains import *
from expert_dollup.core.units import *
from expert_dollup.core.logits import *


class NodeEventDispatcher:
    def __init__(
        self,
        project_service: CollectionService[ProjectDetails],
        project_node_service: CollectionService[ProjectNode],
        node_value_validation: NodeValueValidation,
        project_node_slice_builder: ProjectNodeSliceBuilder,
        project_tree_builder: ProjectTreeBuilder,
        project_node_meta: CollectionService[ProjectNodeMeta],
        formula_resolver: FormulaResolver,
    ):
        self.project_service = project_service
        self.project_node_service = project_node_service
        self.node_value_validation = node_value_validation
        self.project_node_slice_builder = project_node_slice_builder
        self.project_tree_builder = project_tree_builder
        self.project_node_meta = project_node_meta
        self.formula_resolver = formula_resolver

    async def update_node_value(
        self, project_id: UUID, node_id: UUID, value: PrimitiveWithNoneUnion
    ) -> ProjectNode:
        bounded_node = await self._get_bounded_node(project_id, node_id)
        self.node_value_validation.validate_value(bounded_node.definition.config, value)
        await self._execute_triggers(bounded_node, value)
        await self.project_node_service.update(
            ProjectNodeValues(value=value),
            ProjectNodeFilter(project_id=bounded_node.node.project_id, id=node_id),
        )

        return await self.project_node_service.find_by_id(node_id)

    async def update_nodes_value(
        self, project_id: UUID, updates: List[FieldUpdate]
    ) -> List[ProjectNode]:
        nodes: List[ProjectNode] = []

        for update in updates:
            node = await self.update_node_value(
                project_id, update.node_id, update.value
            )
            nodes.append(node)

        return nodes

    async def update_value_inplace(
        self, nodes: List[ProjectNode], metas: List[ProjectNodeMeta]
    ):
        meta_by_names = {meta.definition.name: meta for meta in metas}
        formula_references = []
        for node in nodes:
            meta = meta_by_names[node.type_name]
            field_details = meta.definition.config.field_details

            if isinstance(field_details, StaticNumberFieldConfig):
                formula_references.append(
                    UnitRef(node_id=node.id, path=node.path, name=node.value)
                )

        if len(formula_references) == 0:
            return

        results = await self.formula_resolver.compute_formula(
            node.project_id, meta.definition.project_definition_id, formula_references
        )

        for node, value in zip(nodes, results):
            node.value = str(value)

    async def _get_bounded_node(self, project_id: UUID, node_id: UUID) -> BoundedNode:
        node = await self.project_node_service.find_one_by(
            ProjectNodeFilter(project_id=project_id, id=node_id)
        )

        meta_node: ProjectNodeMeta = await self.project_node_meta.find_one_by(
            ProjectNodeMetaFilter(project_id=node.project_id, type_id=node.type_id)
        )

        node_definition = meta_node.definition

        return BoundedNode(node=node, definition=node_definition)

    async def execute_node_trigger(self, bounded_node: BoundedNode):
        if bounded_node.definition.config:
            await self._execute_triggers(
                bounded_node,
                bounded_node.node.value,
            )

    async def _execute_triggers(
        self, bounded_node: BoundedNode, value: PrimitiveWithNoneUnion
    ) -> None:
        project_id = bounded_node.node.project_id

        for trigger in bounded_node.definition.config.triggers:
            if trigger.action == TriggerAction.SET_VISIBILITY:
                await self._trigger_toogle_visibility(trigger, project_id, value)
            elif trigger.action == TriggerAction.CHANGE_NAME:
                await self._trigger_change_name(trigger, bounded_node, value)

    async def _trigger_toogle_visibility(
        self, trigger: Trigger, project_id: UUID, value: PrimitiveWithNoneUnion
    ):
        meta_node: ProjectNodeMeta = await self.project_node_meta.find_one_by(
            ProjectNodeMetaFilter(project_id=project_id, type_id=trigger.target_type_id)
        )

        meta_node.state.is_visible = bool(value)
        await self.project_node_meta.update(
            ProjectNodeMetaFilter(state=meta_node.state),
            ProjectNodeMetaFilter(
                project_id=project_id, type_id=trigger.target_type_id
            ),
        )

    async def _trigger_change_name(
        self, trigger: Trigger, bounded_node: BoundedNode, value: PrimitiveWithNoneUnion
    ) -> None:
        index = bounded_node.node.type_path.index(trigger.target_type_id)
        path = bounded_node.node.path[0 : index + 1]
        nodes = await self.project_node_service.find_node_on_path_by_type(
            bounded_node.node.project_id, path, trigger.target_type_id
        )

        for node in nodes:
            await self.project_node_service.update(
                ProjectNodeFilter(label=str(value)),
                ProjectNodeFilter(project_id=node.project_id, id=node.id),
            )
