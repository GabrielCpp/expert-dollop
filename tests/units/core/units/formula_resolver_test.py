import pytest
from uuid import UUID
from decimal import Decimal
from tests.fixtures.mock_interface_utils import StrictInterfaceSetup
from expert_dollup.core.object_storage import ObjectStorage
from expert_dollup.shared.database_services import CollectionService
from expert_dollup.core.services import *
from expert_dollup.core.domains import *
from expert_dollup.core.queries import *
from expert_dollup.core.units import *
from expert_dollup.core.builders import *
from tests.fixtures import *


@pytest.mark.asyncio
async def test_given_unit_instances_should_compute_collection(logger_factory):
    project_node_service = StrictInterfaceSetup(ProjectNodeService)
    unit_instance_builder = StrictInterfaceSetup(UnitInstanceBuilder)
    stage_formulas_storage = StrictInterfaceSetup(ObjectStorage)

    fixture = ProjectInstanceFactory.build(make_base_project_seed())
    fields = [node for node in fixture.nodes if not node.value is None]
    stages_formulas = FormulaResolver.stage_formulas(fixture.formulas)

    stage_formulas_storage.setup(
        lambda x: x.load(StagedFormulasKey(fixture.project_definition.id)),
        returns_async=stages_formulas,
    )

    project_node_service.setup(
        lambda x: x.get_all_fields(fixture.project.id), returns_async=fields
    )

    unit_instance_builder.setup(
        lambda x: x.build_with_fields(stages_formulas, fields),
        returns=fixture.unit_instances,
    )

    formula_resolver = FormulaResolver(
        StrictInterfaceSetup(CollectionService).object,
        project_node_service.object,
        StrictInterfaceSetup(ProjectDefinitionNodeService).object,
        unit_instance_builder.object,
        stage_formulas_storage.object,
        logger_factory,
    )

    injector = await formula_resolver.compute_all_project_formula(
        fixture.project.id, fixture.project_definition.id
    )

    assert injector.unit_instances == [
        UnitInstance(
            formula_id=None,
            node_id=UUID("941055cb-b2bc-0916-4182-4774e576c6eb"),
            path=[
                UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
                UUID("6cb8eec4-0e80-2926-8813-79a4aca227cb"),
                UUID("8ceb58ac-94a7-0ae9-a6da-6b6fbb3e00e8"),
                UUID("3951ecfd-e673-f1f3-9618-55470aabd2ca"),
            ],
            name="fieldA",
            calculation_details="",
            result=Decimal("5"),
        ),
        UnitInstance(
            formula_id=None,
            node_id=UUID("a23ee02f-9bc1-0573-ed61-60ebffc6d4c8"),
            path=[
                UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
                UUID("6cb8eec4-0e80-2926-8813-79a4aca227cb"),
                UUID("8ceb58ac-94a7-0ae9-a6da-6b6fbb3e00e8"),
                UUID("9cb49761-6037-097e-6769-64645ffd1679"),
            ],
            name="fieldA",
            calculation_details="",
            result=Decimal("4"),
        ),
        UnitInstance(
            formula_id=None,
            node_id=UUID("56969dee-a7d6-7243-b154-fe4c75334aa9"),
            path=[
                UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
                UUID("6cb8eec4-0e80-2926-8813-79a4aca227cb"),
                UUID("8ceb58ac-94a7-0ae9-a6da-6b6fbb3e00e8"),
                UUID("ba454054-0eac-b387-bdfa-da917b569de5"),
            ],
            name="fieldA",
            calculation_details="",
            result=Decimal("3"),
        ),
        UnitInstance(
            formula_id=None,
            node_id=UUID("4303a404-1c3e-7aca-1261-9b6544363a3e"),
            path=[
                UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
                UUID("6cb8eec4-0e80-2926-8813-79a4aca227cb"),
                UUID("8ceb58ac-94a7-0ae9-a6da-6b6fbb3e00e8"),
                UUID("1df67248-0a52-b8e0-5754-402d9e704dca"),
            ],
            name="fieldB",
            calculation_details="",
            result=Decimal("2"),
        ),
        UnitInstance(
            formula_id=UUID("f1f1e0ff-2344-48bc-e757-8c9dcd3c671e"),
            node_id=UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
            path=[],
            name="formulaA",
            calculation_details="\ntemp1(12) = sum(fieldA)\ntemp2(24) = <fieldB[4303a404-1c3e-7aca-1261-9b6544363a3e], 2> * temp1(12)\n\n<final_result, 24> = temp2(24)",
            result=Decimal("24"),
        ),
        UnitInstance(
            formula_id=UUID("b9af5d87-31a6-3603-85d0-1c849c9f4b44"),
            node_id=UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
            path=[],
            name="formulaB",
            calculation_details="\ntemp1(6.000000) = sum(sectionA_formula)\ntemp2(12.000000) = <fieldB[4303a404-1c3e-7aca-1261-9b6544363a3e], 2> * temp1(6.000000)\n\n<final_result, 12.000000> = temp2(12.000000)",
            result=Decimal("12.000000"),
        ),
        UnitInstance(
            formula_id=UUID("cbaba831-5e3a-aa8b-a7a5-60234fe98b14"),
            node_id=UUID("3951ecfd-e673-f1f3-9618-55470aabd2ca"),
            path=[
                UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
                UUID("6cb8eec4-0e80-2926-8813-79a4aca227cb"),
                UUID("8ceb58ac-94a7-0ae9-a6da-6b6fbb3e00e8"),
            ],
            name="sectionA_formula",
            calculation_details="\ntemp1(3.000000) = <fieldA[941055cb-b2bc-0916-4182-4774e576c6eb], 5> - 2.000000\n\n<final_result, 3.000000> = temp1(3.000000)",
            result=Decimal("3.000000"),
        ),
        UnitInstance(
            formula_id=UUID("cbaba831-5e3a-aa8b-a7a5-60234fe98b14"),
            node_id=UUID("9cb49761-6037-097e-6769-64645ffd1679"),
            path=[
                UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
                UUID("6cb8eec4-0e80-2926-8813-79a4aca227cb"),
                UUID("8ceb58ac-94a7-0ae9-a6da-6b6fbb3e00e8"),
            ],
            name="sectionA_formula",
            calculation_details="\ntemp1(2.000000) = <fieldA[a23ee02f-9bc1-0573-ed61-60ebffc6d4c8], 4> - 2.000000\n\n<final_result, 2.000000> = temp1(2.000000)",
            result=Decimal("2.000000"),
        ),
        UnitInstance(
            formula_id=UUID("cbaba831-5e3a-aa8b-a7a5-60234fe98b14"),
            node_id=UUID("ba454054-0eac-b387-bdfa-da917b569de5"),
            path=[
                UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
                UUID("6cb8eec4-0e80-2926-8813-79a4aca227cb"),
                UUID("8ceb58ac-94a7-0ae9-a6da-6b6fbb3e00e8"),
            ],
            name="sectionA_formula",
            calculation_details="\ntemp1(1.000000) = <fieldA[56969dee-a7d6-7243-b154-fe4c75334aa9], 3> - 2.000000\n\n<final_result, 1.000000> = temp1(1.000000)",
            result=Decimal("1.000000"),
        ),
    ]
