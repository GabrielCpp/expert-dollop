import pytest
from typing import Dict
from tests.fixtures.mock_interface_utils import StrictInterfaceSetup
from expert_dollup.infra.services import *
from expert_dollup.core.domains import *
from expert_dollup.core.queries import *
from expert_dollup.core.units import *
from tests.fixtures import *


@pytest.mark.asyncio
async def test_given_formula_instances_should_compute_collection():
    formula_service = StrictInterfaceSetup(FormulaService)
    project_node_service = StrictInterfaceSetup(ProjectNodeService)
    project_definition_node_service = StrictInterfaceSetup(ProjectNodeService)
    formula_cache_service = StrictInterfaceSetup(FormulaCacheService)
    formulas_plucker = StrictInterfaceSetup(Plucker)
    nodes_plucker = StrictInterfaceSetup(Plucker)

    node_graphs: Dict[str, DefNodeSeed] = ProjectSeed(
        {
            "rootA": DefNodeSeed(
                {
                    "1": NodeSeed(
                        formulas={
                            "formulaA": FormulaSeed(
                                expression="fieldB*fieldA",
                                formula_dependencies=[],
                                node_dependencies=["fieldB", "fieldA"],
                                calculation_details="<fieldB, 2> * sum(<fieldA, 12>)",
                                result=24,
                            )
                        }
                    )
                }
            ),
            "rootB": DefNodeSeed(),
            "subSectionA": DefNodeSeed({"1": NodeSeed(parent="rootA-1")}),
            "formA": DefNodeSeed({"1": NodeSeed(parent="subSectionA-1")}),
            "sectionA": DefNodeSeed(
                {
                    "1": NodeSeed(
                        parent="formA-1",
                        formulas={
                            "sectionA-formula": FormulaSeed(
                                expression="fieldA-2",
                                calculation_details="<fieldA, 5> - 2",
                                formula_dependencies=[],
                                node_dependencies=["fieldA"],
                                result=3,
                            ),
                        },
                    )
                }
            ),
            "fieldA": DefNodeSeed(
                {
                    "1": NodeSeed(parent="sectionA-1", value=5),
                    "2": NodeSeed(parent="sectionA-1", value=4),
                    "3": NodeSeed(parent="sectionA-1", value=3),
                }
            ),
            "sectionB": DefNodeSeed({"1": NodeSeed(parent="formA-1")}),
            "fieldB": DefNodeSeed({"1": NodeSeed(parent="sectionB-1", value=2)}),
        }
    )

    tree_fixture = ProjectInstanceFactory()
    tree_fixture.build(node_graphs)

    fields = [node for node in tree_fixture.nodes if not node.value is None]

    project_node_service.setup(
        lambda x: x.get_all_fields(tree_fixture.project.id), returns_async=fields
    )

    formula_cache_service.setup(
        lambda x: x.find_by(
            FormulaCachedResultFilter(project_id=tree_fixture.project.id)
        ),
        returns_async=tree_fixture.formulas_cache_result,
    )

    formula_cache_service.setup(
        lambda x: x.repopulate(
            tree_fixture.project.id, tree_fixture.formulas_cache_result
        ),
        returns_async=None,
    )

    formulas_plucker.setup(
        lambda x: x.plucks(
            lambda _: True, [c.formula_id for c in tree_fixture.formulas_cache_result]
        ),
        returns_async=tree_fixture.formulas_cache_result,
    )

    nodes_plucker.setup(
        lambda x: x.plucks(
            lambda _: True, [c.node_id for c in tree_fixture.formulas_cache_result]
        ),
        returns_async=tree_fixture.formulas_cache_result,
    )

    formula_resolver = FormulaResolver(
        formula_service.object,
        project_node_service.object,
        project_definition_node_service.object,
        formula_cache_service.object,
        formulas_plucker.object,
        nodes_plucker.object,
    )

    await formula_resolver.compute_all_project_formula(
        tree_fixture.project.id, tree_fixture.project_definition.id
    )
