import pytest
from uuid import UUID
from tests.fixtures.mock_interface_utils import StrictInterfaceSetup, compare_per_arg
from expert_dollup.infra.services import *
from expert_dollup.core.domains import *
from expert_dollup.core.queries import *
from expert_dollup.core.units import *
from tests.fixtures import *

project_seed = ProjectSeed(
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
                        ),
                        "formulaB": FormulaSeed(
                            expression="fieldB*sectionA_formula",
                            formula_dependencies=["sectionA_formula"],
                            node_dependencies=["fieldB"],
                        ),
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
                        "sectionA_formula": FormulaSeed(
                            expression="fieldA-2",
                            formula_dependencies=[],
                            node_dependencies=["fieldA"],
                        ),
                    },
                ),
                "2": NodeSeed(
                    parent="formA-1",
                    formulas={
                        "sectionA_formula": FormulaSeed(
                            expression="fieldA-2",
                            formula_dependencies=[],
                            node_dependencies=["fieldA"],
                        ),
                    },
                ),
                "3": NodeSeed(
                    parent="formA-1",
                    formulas={
                        "sectionA_formula": FormulaSeed(
                            expression="fieldA-2",
                            formula_dependencies=[],
                            node_dependencies=["fieldA"],
                        ),
                    },
                ),
            }
        ),
        "fieldA": DefNodeSeed(
            {
                "1": NodeSeed(
                    parent="sectionA-1",
                    value=5,
                ),
                "2": NodeSeed(
                    parent="sectionA-2",
                    value=4,
                ),
                "3": NodeSeed(
                    parent="sectionA-3",
                    value=3,
                ),
            }
        ),
        "sectionB": DefNodeSeed({"1": NodeSeed(parent="formA-1")}),
        "fieldB": DefNodeSeed({"1": NodeSeed(parent="sectionB-1", value=2)}),
    }
)


@pytest.mark.asyncio
async def test_given_formula_instances_should_compute_collection():
    formula_service = StrictInterfaceSetup(FormulaService)
    project_node_service = StrictInterfaceSetup(ProjectNodeService)
    project_definition_node_service = StrictInterfaceSetup(ProjectNodeService)
    formula_cache_service = StrictInterfaceSetup(FormulaCacheService)
    formulas_plucker = StrictInterfaceSetup(Plucker)
    nodes_plucker = StrictInterfaceSetup(Plucker)

    fixture = ProjectInstanceFactory.build(project_seed)
    fields = [node for node in fixture.nodes if not node.value is None]

    project_node_service.setup(
        lambda x: x.get_all_fields(fixture.project.id), returns_async=fields
    )

    formula_cache_service.setup(
        lambda x: x.find_by(FormulaCachedResultFilter(project_id=fixture.project.id)),
        returns_async=fixture.formulas_cache_result,
    )

    formula_cache_service.setup(
        lambda x: x.repopulate(fixture.project.id, lambda _: True),
        returns_async=None,
        compare_method=compare_per_arg,
    )

    formulas_plucker.setup(
        lambda x: x.plucks(
            lambda _: True,
            list(set(c.formula_id for c in fixture.formulas_cache_result)),
        ),
        returns_async=fixture.formulas,
    )

    nodes_plucker.setup(
        lambda x: x.plucks(
            lambda _: True, [c.node_id for c in fixture.formulas_cache_result]
        ),
        returns_async=fixture.nodes,
    )

    formula_resolver = FormulaResolver(
        formula_service.object,
        project_node_service.object,
        project_definition_node_service.object,
        formula_cache_service.object,
        formulas_plucker.object,
        nodes_plucker.object,
    )

    results = await formula_resolver.compute_all_project_formula(
        fixture.project.id, fixture.project_definition.id
    )

    assert results == [
        FormulaCachedResult(
            project_id=UUID("10b75052-eb7b-8984-b934-6eae1d6feecc"),
            formula_id=UUID("f1f1e0ff-2344-48bc-e757-8c9dcd3c671e"),
            node_id=UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
            calculation_details="<fieldB, 2> * sum(<fieldA, 12>)",
            result=24,
        ),
        FormulaCachedResult(
            project_id=UUID("10b75052-eb7b-8984-b934-6eae1d6feecc"),
            formula_id=UUID("b9af5d87-31a6-3603-85d0-1c849c9f4b44"),
            node_id=UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
            calculation_details="<fieldB, 2> * sum(<sectionA_formula, 6>)",
            result=12,
        ),
        FormulaCachedResult(
            project_id=UUID("10b75052-eb7b-8984-b934-6eae1d6feecc"),
            formula_id=UUID("cbaba831-5e3a-aa8b-a7a5-60234fe98b14"),
            node_id=UUID("3951ecfd-e673-f1f3-9618-55470aabd2ca"),
            calculation_details="<fieldA, 5> - 2",
            result=3,
        ),
        FormulaCachedResult(
            project_id=UUID("10b75052-eb7b-8984-b934-6eae1d6feecc"),
            formula_id=UUID("cbaba831-5e3a-aa8b-a7a5-60234fe98b14"),
            node_id=UUID("9cb49761-6037-097e-6769-64645ffd1679"),
            calculation_details="<fieldA, 4> - 2",
            result=2,
        ),
        FormulaCachedResult(
            project_id=UUID("10b75052-eb7b-8984-b934-6eae1d6feecc"),
            formula_id=UUID("cbaba831-5e3a-aa8b-a7a5-60234fe98b14"),
            node_id=UUID("ba454054-0eac-b387-bdfa-da917b569de5"),
            calculation_details="<fieldA, 3> - 2",
            result=1,
        ),
    ]
