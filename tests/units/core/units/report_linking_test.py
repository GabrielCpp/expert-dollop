import pytest
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from expert_dollup.core.object_storage import ObjectStorage
from expert_dollup.shared.starlette_injection.clock_provider import StaticClock
from tests.fixtures.mock_interface_utils import (
    StrictInterfaceSetup,
    compare_per_arg,
)
from expert_dollup.app.dtos import *
from expert_dollup.core.units import *
from expert_dollup.core.builders import *
from expert_dollup.core.domains import *
from expert_dollup.core.queries import *
from expert_dollup.core.exceptions import *
from expert_dollup.infra.services import *
from tests.fixtures import *


def make_general_report(project_def_id: UUID) -> ReportDefinition:
    return ReportDefinitionFactory(
        project_def_id=project_def_id,
        name="general_report",
        structure=ReportStructure(
            columns=[
                ReportComputation(
                    name="post_transform_factor",
                    expression="1.0",
                    is_visible=False,
                ),
                ReportComputation(
                    name="stage",
                    expression="row['floor']['name']",
                ),
                ReportComputation(
                    name="substage_description",
                    expression="row['substage']['name']",
                ),
                ReportComputation(
                    name="abstract_product_description",
                    expression="row['abstractproduct']['name']",
                ),
                ReportComputation(
                    name="cost_per_unit",
                    expression="round_number(row['datasheet_element']['price'], 2, 'truncate')",
                ),
                ReportComputation(
                    name="result",
                    expression="sum(row['formula']['result'] * row['columns']['post_transform_factor'] for row in rows)",
                ),
                ReportComputation(
                    name="cost",
                    expression="round_number( round_number( sum(row['formula']['result'] * row['columns']['post_transform_factor'] for row in rows), 2, 'truncate') * row['datasheet_element']['price'], 2, 'truncate')",
                ),
                ReportComputation(
                    name="order_form_category_description",
                    expression="row['orderformcategory']['name']",
                ),
            ],
            datasheet_selection_alias="abstractproduct",
            joins_cache=[],
            stage_summary=StageSummary(
                label=AttributeBucket(bucket_name="columns", attribute_name="stage"),
                summary=ReportComputation(
                    expression="sum(row['cost'] for row in rows)",
                    unit="$",
                    name="total",
                ),
            ),
            report_summary=[],
            formula_attribute=AttributeBucket(
                bucket_name="substage", attribute_name="formula"
            ),
            datasheet_attribute=AttributeBucket(
                bucket_name="substage", attribute_name="datasheet_element"
            ),
            group_by=[
                AttributeBucket("columns", "stage"),
                AttributeBucket("columns", "substage_description"),
                AttributeBucket("columns", "abstract_product_description"),
                AttributeBucket("columns", "order_form_category_description"),
            ],
            order_by=[
                AttributeBucket("stage", "order_index"),
                AttributeBucket("substage", "order_index"),
            ],
        ),
    )


@pytest.mark.asyncio
async def test_given_row_cache_should_produce_correct_report():
    project_seed = make_base_project_seed()
    datasheet_fixture = DatasheetInstanceFactory.build(
        make_base_datasheet(project_seed)
    )
    project_fixture = ProjectInstanceFactory.build(
        project_seed,
        default_datasheet_id=datasheet_fixture.datasheet.id,
        datasheet_def_id=datasheet_fixture.datasheet_definition.id,
    )

    report_definition = make_general_report(project_fixture.project_definition.id)
    report_rows_cache = [
        {
            "abstractproduct": {
                "id": UUID("9edcbbf4-3696-80e9-59b5-aa8c5f94958b"),
                "is_collection": False,
                "name": "wood_plank",
                "order_index": 0,
                "tags": [UUID("b24c883f-5831-cc9d-3607-d292d265af9a")],
                "unit_id": "m",
            },
            "floor": {
                "id": UUID("6524c49c-93e7-0606-4d62-1ac982d40027"),
                "name": "floor_label_0",
                "order_index": 0,
            },
        }
    ]

    report_def_row_cache = StrictInterfaceSetup(ObjectStorage)
    datasheet_element_service = StrictInterfaceSetup(DatasheetElementService)
    expression_evaluator = StrictInterfaceSetup(ExpressionEvaluator)
    report_row_cache = StrictInterfaceSetup(ReportRowCache)
    formula_resolver = StrictInterfaceSetup(FormulaResolver)
    clock = StaticClock(datetime(2000, 4, 3, 1, 1, 1, 7, timezone.utc))

    report_def_row_cache.setup(
        lambda x: x.load(
            ReportRowKey(
                project_def_id=report_definition.project_def_id,
                report_definition_id=report_definition.id,
            )
        ),
        returns_async=report_rows_cache,
    )

    expression_evaluator.setup(
        lambda x: x.evaluate(
            next(
                c.expression
                for c in report_definition.structure.columns
                if c.name == "cost"
            ),
            lambda y: True,
        ),
        returns=Decimal(123),
        compare_method=compare_per_arg,
    )

    expression_evaluator.setup(
        lambda x: x.evaluate(
            lambda y: True,
            lambda y: True,
        ),
        returns="for test sake",
        compare_method=compare_per_arg,
    )

    report_linking = ReportLinking(
        datasheet_element_service.object,
        expression_evaluator.object,
        report_row_cache.object,
        formula_resolver.object,
        clock,
    )

    report_rows = await report_linking.link_report(
        report_definition, project_fixture.project
    )

    expected_rows = Report(
        stages=[
            ReportStage(
                label="for test sake",
                summary="for test sake",
                rows=[
                    ReportRow(
                        project_id=UUID("10b75052-eb7b-8984-b934-6eae1d6feecc"),
                        report_def_id=report_definition.id,
                        node_id=UUID("3e9245a2-855a-eca6-ebba-ce294ba5575d"),
                        formula_id=UUID("f1f1e0ff-2344-48bc-e757-8c9dcd3c671e"),
                        group_digest="651cd4366315963309a16b457b4974c3fd0e45f96ed365516936a0ad6bd92823",
                        order_index=0,
                        datasheet_id=UUID("098f6bcd-4621-d373-cade-4e832627b4f6"),
                        element_id=UUID("9edcbbf4-3696-80e9-59b5-aa8c5f94958b"),
                        child_reference_id=UUID("00000000-0000-0000-0000-000000000000"),
                        row={
                            "abstractproduct": {
                                "id": UUID("9edcbbf4-3696-80e9-59b5-aa8c5f94958b"),
                                "is_collection": False,
                                "name": "wood_plank",
                                "order_index": 0,
                                "tags": [UUID("b24c883f-5831-cc9d-3607-d292d265af9a")],
                                "unit_id": "m",
                            },
                            "floor": {
                                "id": UUID("6524c49c-93e7-0606-4d62-1ac982d40027"),
                                "name": "floor_label_0",
                                "order_index": 0,
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
                            "orderformcategory": {
                                "id": UUID("444ea1f0-5338-5998-265d-1700d4327f51"),
                                "name": "orderformcategory_label_0",
                                "order_index": 0,
                                "worksection": UUID(
                                    "407be730-a7a7-9d39-183f-85a1b8017b47"
                                ),
                            },
                            "productcategory": {
                                "id": UUID("b24c883f-5831-cc9d-3607-d292d265af9a"),
                                "name": "productcategory_label_0",
                                "order_index": 0,
                            },
                            "stage": {
                                "associated_global_section": "value0",
                                "compile_in_one": True,
                                "floor": UUID("6524c49c-93e7-0606-4d62-1ac982d40027"),
                                "id": UUID("68e30dbc-7508-6e56-8a1e-59ee389483d9"),
                                "localisation": "value0",
                                "name": "stage_label_0",
                                "order_index": 0,
                            },
                            "substage": {
                                "datasheet_element": UUID(
                                    "9edcbbf4-3696-80e9-59b5-aa8c5f94958b"
                                ),
                                "formula": UUID("f1f1e0ff-2344-48bc-e757-8c9dcd3c671e"),
                                "id": UUID("6fce3c97-2660-2ad4-9f6f-4c4921c8c59b"),
                                "name": "substage_label_0",
                                "order_index": 0,
                                "orderformcategory": UUID(
                                    "444ea1f0-5338-5998-265d-1700d4327f51"
                                ),
                                "quantity": "0",
                                "special_condition": True,
                                "stage": UUID("68e30dbc-7508-6e56-8a1e-59ee389483d9"),
                            },
                            "worksection": {
                                "id": UUID("407be730-a7a7-9d39-183f-85a1b8017b47"),
                                "name": "worksection_label_0",
                                "order_index": 0,
                            },
                            "datasheet_element": {
                                "price": Decimal("0"),
                                "factor": Decimal("0"),
                                "element_def_id": UUID(
                                    "9edcbbf4-3696-80e9-59b5-aa8c5f94958b"
                                ),
                                "child_element_reference": UUID(
                                    "00000000-0000-0000-0000-000000000000"
                                ),
                                "original_datasheet_id": UUID(
                                    "098f6bcd-4621-d373-cade-4e832627b4f6"
                                ),
                            },
                            "columns": {
                                "post_transform_factor": "for test sake",
                                "stage": "for test sake",
                                "substage_description": "for test sake",
                                "abstract_product_description": "for test sake",
                                "order_form_category_description": "for test sake",
                                "cost_per_unit": "for test sake",
                                "result": "for test sake",
                                "cost": Decimal("123"),
                            },
                        },
                    )
                ],
            )
        ],
        creation_date_utc=datetime(2000, 4, 3, 1, 1, 1, 7, tzinfo=timezone.utc),
    )

    assert report_rows == expected_rows
