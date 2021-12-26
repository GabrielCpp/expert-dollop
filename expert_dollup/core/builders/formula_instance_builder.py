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
                        formula_dependencies=formula.dependency_graph.dependencies,
                        calculation_details="<was not calculated yet>",
                        result=0,
                    )
                )

        return formulas_result