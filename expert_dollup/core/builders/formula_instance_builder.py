from typing import List, Dict
from uuid import UUID
from collections import defaultdict
from expert_dollup.core.queries import Plucker
from expert_dollup.infra.services import FormulaService
from expert_dollup.core.domains import *
from expert_dollup.core.logits import serialize_post_processed_expression


class FormulaInstanceBuilder:
    def __init__(self, formula_plucker: Plucker[FormulaService]):
        self.formula_plucker = formula_plucker

    async def build(
        self,
        project_def_id: UUID,
        nodes: List[ProjectNode],
    ) -> List[FormulaInstance]:
        formulas_result: List[FormulaInstance] = []
        nodes_by_type_id: Dict[UUID, List[ProjectNode]] = defaultdict(list)

        for node in nodes:
            nodes_by_type_id[node.type_id].append(node)

        formulas = await self.formula_plucker.pluck_subressources(
            FormulaFilter(project_def_id=project_def_id),
            lambda ids: FormulaPluckFilter(attached_to_type_ids=ids),
            list(nodes_by_type_id.keys()),
        )

        for formula in formulas:
            assert formula.attached_to_type_id in nodes_by_type_id
            nodes = nodes_by_type_id.get(formula.attached_to_type_id)

            for node in nodes:
                formulas_result.append(
                    FormulaInstance(
                        project_id=node.project_id,
                        formula_id=formula.id,
                        node_id=node.id,
                        node_path=node.path,
                        formula_name=formula.name,
                        calculation_details="<was not calculated yet>",
                        result=0,
                    )
                )

        return formulas_result

    def build_with_fields(
        self, formulas: List[Formula], nodes: List[ProjectNode]
    ) -> List[FormulaInstance]:
        formulas_result: List[FormulaInstance] = []
        parent_node_by_type_id = defaultdict(list)
        project_id = nodes[0].project_id
        done_nodes = set()
        skipped_formulas = set()

        for node in nodes:
            assert node.project_id == project_id
            assert len(node.path) == 4

            for index in range(0, len(node.path)):
                node_id = node.path[index]

                if node_id in done_nodes:
                    continue

                done_nodes.add(node_id)
                parent_node_by_type_id[node.type_path[index]].append(
                    (node_id, [] if index == 0 else node.path[0:index])
                )

        for formula in formulas:
            if not formula.attached_to_type_id in parent_node_by_type_id:
                skipped_formulas.add(formula.attached_to_type_id)
                continue

            parent_nodes = parent_node_by_type_id[formula.attached_to_type_id]

            for node_id, node_path in parent_nodes:
                formulas_result.append(
                    FormulaInstance(
                        project_id=project_id,
                        formula_id=formula.id,
                        node_id=node_id,
                        node_path=node_path,
                        formula_name=formula.name,
                        calculation_details="<was not calculated yet>",
                        result=0,
                    )
                )

        print(skipped_formulas)

        return formulas_result
