import pytest
from datetime import datetime, timezone
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID
from expert_dollup.core.logits import FormulaInjector, FrozenUnit
from expert_dollup.shared.starlette_injection.clock_provider import StaticClock
from tests.fixtures.factories.datasheet_factory import CustomDatasheetInstancePackage
from tests.fixtures.factories.project_instance_factory import (
    CustomProjectInstancePackage,
)
from tests.fixtures.mock_interface_utils import StrictInterfaceSetup
from expert_dollup.app.dtos import *
from expert_dollup.core.units import *
from expert_dollup.core.builders import *
from expert_dollup.core.domains import *
from expert_dollup.core.queries import *
from expert_dollup.core.exceptions import *
from expert_dollup.infra.services import *
from tests.fixtures import *


@dataclass
class ReportSeed:
    project_seed: ProjectSeed
    datasheet_fixture: CustomDatasheetInstancePackage
    project_fixture: CustomProjectInstancePackage
    report_definition: ReportDefinition
    element_def: DatasheetDefinitionElement
    datasheet_element: DatasheetElement
    formula: Formula


@pytest.fixture
def report_seed() -> ReportSeed:
    project_seed = make_base_project_seed()
    datasheet_fixture = DatasheetInstanceFactory.build(
        make_base_datasheet(project_seed)
    )
    project_fixture = ProjectInstanceFactory.build(
        project_seed,
        default_datasheet_id=datasheet_fixture.datasheet.id,
        datasheet_def_id=datasheet_fixture.datasheet_definition.id,
    )
    report_definition = ReportDefinitionFactory(
        project_def_id=project_fixture.project_definition.id
    )

    element_def = next(
        datasheet_definition_element
        for datasheet_definition_element in datasheet_fixture.datasheet_definition_elements
        if datasheet_definition_element.name == "concrete"
    )
    datasheet_element = next(
        datasheet_element
        for datasheet_element in datasheet_fixture.datasheet_elements
        if datasheet_element.element_def_id == element_def.id
    )

    formula = next(
        formula for formula in project_fixture.formulas if formula.name == "formulaA"
    )

    return ReportSeed(
        project_seed=project_seed,
        datasheet_fixture=datasheet_fixture,
        project_fixture=project_fixture,
        report_definition=report_definition,
        element_def=element_def,
        datasheet_element=datasheet_element,
        formula=formula,
    )


@pytest.mark.asyncio
async def test_given_row_cache_should_produce_correct_report(
    report_seed: ReportSeed, logger_factory
):
    element_def = report_seed.element_def
    datasheet_element = report_seed.datasheet_element
    formula = report_seed.formula
    project_fixture = report_seed.project_fixture
    datasheet_fixture = report_seed.datasheet_fixture
    report_definition = report_seed.report_definition
    report_rows_cache = [
        {
            "abstractproduct": element_def.report_dict,
            "datasheet_element": datasheet_element.report_dict,
            "formula": formula.report_dict,
            "stage": {"name": "show_concrete"},
            "substage": {
                "id": UUID("6524c49c-93e7-0606-4d62-1ac982d40027"),
                "name": "floor_label_0",
                "order_index": 0,
                "datasheet_element": element_def.id,
                "formula": formula.id,
            },
        }
    ]

    datasheet_element_service = StrictInterfaceSetup(DatasheetElementService)
    report_row_cache = StrictInterfaceSetup(ReportRowCache)
    formula_resolver = StrictInterfaceSetup(FormulaResolver)
    clock = StaticClock(datetime(2000, 4, 3, 1, 1, 1, 0, timezone.utc))

    report_row_cache.setup(
        lambda x: x.refresh_cache(report_definition), returns_async=report_rows_cache
    )

    formula_resolver.setup(
        lambda x: x.compute_all_project_formula(
            project_fixture.project.id, report_definition.project_def_id
        ),
        returns_async=FormulaInjector().add_units(
            FrozenUnit(i) for i in project_fixture.unit_instances
        ),
    )

    datasheet_element_service.setup(
        lambda x: x.find_by(
            DatasheetElementFilter(
                datasheet_id=datasheet_fixture.datasheet.id,
                child_element_reference=zero_uuid(),
            )
        ),
        returns_async=[
            datasheet_element
            for datasheet_element in datasheet_fixture.datasheet_elements
            if datasheet_element.child_element_reference == zero_uuid()
        ],
    )

    report_linking = ReportLinking(
        datasheet_element_service.object,
        ExpressionEvaluator(),
        report_row_cache.object,
        formula_resolver.object,
        clock,
        logger_factory,
    )

    report = await report_linking.link_report(
        report_definition, project_fixture.project
    )

    assert report == Report(
        stages=[
            ReportStage(
                summary=ComputedValue(
                    label="show_concrete", value=Decimal("24.24"), unit="unit"
                ),
                rows=[
                    ReportRow(
                        node_id=UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
                        formula_id=UUID("f1f1e0ff-2344-48bc-e757-8c9dcd3c671e"),
                        element_def_id=UUID("00ecf6d0-6f00-c4bb-2902-4057469a3f3d"),
                        child_reference_id=UUID("00000000-0000-0000-0000-000000000000"),
                        columns=[
                            ReportColumn(value="show_concrete", unit="unit"),
                            ReportColumn(value=Decimal("24"), unit="unit"),
                            ReportColumn(value="concrete", unit="unit"),
                            ReportColumn(value=Decimal("1.01"), unit="$"),
                            ReportColumn(value=Decimal("24.24"), unit="$"),
                        ],
                        row={
                            "abstractproduct": {
                                "id": UUID("00ecf6d0-6f00-c4bb-2902-4057469a3f3d"),
                                "unit_id": "m",
                                "is_collection": False,
                                "order_index": 1,
                                "name": "concrete",
                            },
                            "datasheet_element": {
                                "id": UUID("00ecf6d0-6f00-c4bb-2902-4057469a3f3d"),
                                "unit_id": "m",
                                "is_collection": False,
                                "order_index": 1,
                                "name": "concrete",
                                "price": Decimal("1.01"),
                                "factor": Decimal("1.01"),
                                "element_def_id": UUID(
                                    "00ecf6d0-6f00-c4bb-2902-4057469a3f3d"
                                ),
                                "child_element_reference": UUID(
                                    "00000000-0000-0000-0000-000000000000"
                                ),
                                "original_datasheet_id": UUID(
                                    "098f6bcd-4621-d373-cade-4e832627b4f6"
                                ),
                            },
                            "formula": {
                                "formula_id": UUID(
                                    "f1f1e0ff-2344-48bc-e757-8c9dcd3c671e"
                                ),
                                "node_id": UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
                                "path": [],
                                "name": "formulaA",
                                "calculation_details": "<fieldB, 2> * sum(<fieldA, 12>)",
                                "result": Decimal("24"),
                            },
                            "stage": {"name": "show_concrete"},
                            "substage": {
                                "id": UUID("6524c49c-93e7-0606-4d62-1ac982d40027"),
                                "name": "floor_label_0",
                                "order_index": 0,
                                "datasheet_element": UUID(
                                    "00ecf6d0-6f00-c4bb-2902-4057469a3f3d"
                                ),
                                "formula": UUID("f1f1e0ff-2344-48bc-e757-8c9dcd3c671e"),
                            },
                            "columns": {
                                "stage": "show_concrete",
                                "product_name": "concrete",
                                "quantity": Decimal("24"),
                                "cost_per_unit": Decimal("1.01"),
                                "cost": Decimal("24.24"),
                            },
                            "internal": {
                                "group_digest": "show_concrete/concrete",
                                "order_index": 0,
                            },
                        },
                    )
                ],
            )
        ],
        summaries=[ComputedValue(label="subtotal", value=Decimal("24.24"), unit="$")],
        creation_date_utc=datetime(2000, 4, 3, 1, 1, 1, 0, tzinfo=timezone.utc),
    )
