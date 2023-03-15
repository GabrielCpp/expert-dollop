import pytest
from uuid import UUID
from decimal import Decimal
from tests.fixtures.mock_interface_utils import StrictInterfaceSetup
from expert_dollup.shared.database_services import Repository
from expert_dollup.core.repositories import *
from expert_dollup.core.domains import *
from expert_dollup.core.units import *
from expert_dollup.core.units.evaluator import *
from expert_dollup.core.builders import *
from tests.fixtures import *


@pytest.mark.asyncio
async def test_given_unit_instances_should_compute_collection(logger_factory):
    project_node_service = StrictInterfaceSetup(ProjectNodeRepository)
    stage_formulas_storage = StrictInterfaceSetup(Repository)

    fixture = ProjectInstanceFactory.build(make_base_project_seed())
    fields = [node for node in fixture.nodes if not node.value is None]
    compiler = ExpressionCompiler.create_simple()
    stages_formulas = [
        StagedFormula.from_formula(formula, compiler.compile_to_dict)
        for formula in fixture.formulas
    ]

    expected_result = [
        Unit(
            node_id=UUID("941055cb-b2bc-0916-4182-4774e576c6eb"),
            path=[
                UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
                UUID("6cb8eec4-0e80-2926-8813-79a4aca227cb"),
                UUID("8ceb58ac-94a7-0ae9-a6da-6b6fbb3e00e8"),
                UUID("3951ecfd-e673-f1f3-9618-55470aabd2ca"),
            ],
            name="fieldA",
            calculation_details="",
            value=Decimal("5"),
        ),
        Unit(
            node_id=UUID("a23ee02f-9bc1-0573-ed61-60ebffc6d4c8"),
            path=[
                UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
                UUID("6cb8eec4-0e80-2926-8813-79a4aca227cb"),
                UUID("8ceb58ac-94a7-0ae9-a6da-6b6fbb3e00e8"),
                UUID("9cb49761-6037-097e-6769-64645ffd1679"),
            ],
            name="fieldA",
            calculation_details="",
            value=Decimal("4"),
        ),
        Unit(
            node_id=UUID("56969dee-a7d6-7243-b154-fe4c75334aa9"),
            path=[
                UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
                UUID("6cb8eec4-0e80-2926-8813-79a4aca227cb"),
                UUID("8ceb58ac-94a7-0ae9-a6da-6b6fbb3e00e8"),
                UUID("ba454054-0eac-b387-bdfa-da917b569de5"),
            ],
            name="fieldA",
            calculation_details="",
            value=Decimal("3"),
        ),
        Unit(
            node_id=UUID("4303a404-1c3e-7aca-1261-9b6544363a3e"),
            path=[
                UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
                UUID("6cb8eec4-0e80-2926-8813-79a4aca227cb"),
                UUID("8ceb58ac-94a7-0ae9-a6da-6b6fbb3e00e8"),
                UUID("1df67248-0a52-b8e0-5754-402d9e704dca"),
            ],
            name="fieldB",
            calculation_details="",
            value=Decimal("2"),
        ),
        Unit(
            node_id=UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
            path=[],
            name="formulaA",
            dependencies=["fieldB", "fieldA"],
            calculation_details="\ntemp1(24) = <fieldB[4303a404-1c3e-7aca-1261-9b6544363a3e], 2> * <12, sum(fieldA)>\n\n<final_result, 24> = temp1(24)",
            value=Decimal("24"),
        ),
        Unit(
            node_id=UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
            path=[],
            name="formulaB",
            dependencies=["sectionA_formula", "fieldB"],
            calculation_details="\ntemp1(12) = <fieldB[4303a404-1c3e-7aca-1261-9b6544363a3e], 2> * <6, sum(sectionA_formula)>\n\n<final_result, 12> = temp1(12)",
            value=Decimal("12"),
        ),
        Unit(
            node_id=UUID("3951ecfd-e673-f1f3-9618-55470aabd2ca"),
            path=[
                UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
                UUID("6cb8eec4-0e80-2926-8813-79a4aca227cb"),
                UUID("8ceb58ac-94a7-0ae9-a6da-6b6fbb3e00e8"),
            ],
            name="sectionA_formula",
            dependencies=["fieldA"],
            calculation_details="\ntemp1(3) = <fieldA[941055cb-b2bc-0916-4182-4774e576c6eb], 5> - 2\n\n<final_result, 3> = temp1(3)",
            value=Decimal("3"),
        ),
        Unit(
            node_id=UUID("9cb49761-6037-097e-6769-64645ffd1679"),
            path=[
                UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
                UUID("6cb8eec4-0e80-2926-8813-79a4aca227cb"),
                UUID("8ceb58ac-94a7-0ae9-a6da-6b6fbb3e00e8"),
            ],
            name="sectionA_formula",
            dependencies=["fieldA"],
            calculation_details="\ntemp1(2) = <fieldA[a23ee02f-9bc1-0573-ed61-60ebffc6d4c8], 4> - 2\n\n<final_result, 2> = temp1(2)",
            value=Decimal("2"),
        ),
        Unit(
            node_id=UUID("ba454054-0eac-b387-bdfa-da917b569de5"),
            path=[
                UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
                UUID("6cb8eec4-0e80-2926-8813-79a4aca227cb"),
                UUID("8ceb58ac-94a7-0ae9-a6da-6b6fbb3e00e8"),
            ],
            name="sectionA_formula",
            dependencies=["fieldA"],
            calculation_details="\ntemp1(1) = <fieldA[56969dee-a7d6-7243-b154-fe4c75334aa9], 3> - 2\n\n<final_result, 1> = temp1(1)",
            value=Decimal("1"),
        ),
    ]

    stage_formulas_storage.setup(
        lambda x: x.find(fixture.project_definition.id),
        returns_async=stages_formulas,
    )

    project_node_service.setup(
        lambda x: x.get_all_fields(fixture.project.id), returns_async=fields
    )

    formula_resolver = FormulaResolver(
        StrictInterfaceSetup(Repository).object,
        project_node_service.object,
        StrictInterfaceSetup(ProjectDefinitionNodeRepository).object,
        stage_formulas_storage.object,
        compiler,
        logger_factory,
    )

    injector = await formula_resolver.compute_all_project_formula(
        fixture.project.id, fixture.project_definition.id
    )
    for r in injector.units:
        r.computable = None

    assert injector.units == expected_result
