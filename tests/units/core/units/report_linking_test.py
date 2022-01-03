import pytest
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from expert_dollup.core.object_storage import ObjectStorage
from expert_dollup.shared.starlette_injection.clock_provider import StaticClock
from tests.fixtures.mock_interface_utils import (
    StrictInterfaceSetup,
    compare_per_arg,
    raise_async,
)
from expert_dollup.app.dtos import *
from expert_dollup.core.units import *
from expert_dollup.core.builders import *
from expert_dollup.core.domains import *
from expert_dollup.core.queries import *
from expert_dollup.core.exceptions import *
from expert_dollup.infra.services import *
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


datasheet_seed = DatasheetSeed(
    properties={"price": Decimal, "factor": Decimal},
    element_seeds={
        "wood_plank": ElementSeed(
            tags=["productcategory_label_0"],
            unit_id="m",
        ),
        "concrete": ElementSeed(
            tags=["productcategory_label_1"],
            unit_id="m",
        ),
        "ceramix": ElementSeed(
            tags=["productcategory_label_2"], unit_id="m", is_collection=True
        ),
    },
    collection_seeds={
        "substage": CollectionSeed(
            label_count=10,
            schemas={
                "formula": FormulaAggregate("*"),
                "special_condition": bool,
                "quantity": Decimal,
                "stage": CollectionAggregate("stage"),
                "orderformcategory": CollectionAggregate("orderformcategory"),
                "datasheet_element": DatasheetAggregate("*"),
            },
        ),
        "stage": CollectionSeed(
            label_count=5,
            schemas={
                "localisation": str,
                "associated_global_section": str,
                "compile_in_one": bool,
                "floor": CollectionAggregate("floor"),
            },
        ),
        "orderformcategory": CollectionSeed(
            label_count=3, schemas={"worksection": CollectionAggregate("worksection")}
        ),
        "worksection": CollectionSeed(label_count=3),
        "productcategory": CollectionSeed(label_count=3),
        "floor": CollectionSeed(label_count=3),
    },
    formulas=project_seed.formulas,
)

post_transform_factor_snippet = """
def get_post_transform_factor(unit_id, conversion_factor, special_condition):
    linear_unit_id = "linearunit" # 2
    brick_to_foot_id = "bricktofoot" # 11
    mul_conversion_factor = 1.0

    if (unit_id == linear_unit_id and special_condition) or unit_id != linear_unit_id:
        mul_conversion_factor = conversion_factor

    if mul_conversion_factor == 0:
        mul_conversion_factor = 1
    elif unit_id != brick_to_foot_id:
        mul_conversion_factor = 1/mul_conversion_factor
    
    return round_number(mul_conversion_factor, 8, 'truncate')


get_post_transform_factor(row['abstractproduct']['unit_id'], row['datasheet_element']['factor'], row['substage']['special_condition'])
"""


def make_general_report(project_def_id: UUID) -> ReportDefinition:
    return ReportDefinitionFactory(
        project_def_id=project_def_id,
        name="general_report",
        structure=ReportStructure(
            columns=[
                ReportColumn(
                    name="post_transform_factor",
                    expression=post_transform_factor_snippet,
                    is_visible=False,
                ),
                ReportColumn(
                    name="stage",
                    expression="row['floor']['name']",
                ),
                ReportColumn(
                    name="substage_description",
                    expression="row['substage']['name']",
                ),
                ReportColumn(
                    name="abstract_product_description",
                    expression="row['abstractproduct']['name']",
                ),
                ReportColumn(
                    name="cost_per_unit",
                    expression="round_number(row['datasheet_element']['price'], 2, 'truncate')",
                ),
                ReportColumn(
                    name="result",
                    expression="sum(row['formula']['result'] * row['columns']['post_transform_factor'] for row in rows)",
                ),
                ReportColumn(
                    name="cost",
                    expression="round_number( round_number( sum(row['formula']['result'] * row['columns']['post_transform_factor'] for row in rows), 2, 'truncate') * row['datasheet_element']['price'], 2, 'truncate')",
                ),
                ReportColumn(
                    name="order_form_category_description",
                    expression="row['orderformcategory']['name']",
                ),
            ],
            datasheet_selection_alias="abstractproduct",
            joins_cache=[
                ReportJoin(
                    from_object_name="abstractproduct",
                    from_property_name="id",
                    join_on_collection="substage",
                    join_on_attribute="datasheet_element",
                    alias_name="substage",
                ),
                ReportJoin(
                    from_object_name="substage",
                    from_property_name="stage",
                    join_on_collection="stage",
                    join_on_attribute="id",
                    alias_name="stage",
                ),
                ReportJoin(
                    from_object_name="stage",
                    from_property_name="floor",
                    join_on_collection="floor",
                    join_on_attribute="id",
                    alias_name="floor",
                ),
                ReportJoin(
                    from_object_name="abstractproduct",
                    from_property_name="tags",
                    join_on_collection="productcategory",
                    join_on_attribute="id",
                    alias_name="productcategory",
                ),
                ReportJoin(
                    from_object_name="substage",
                    from_property_name="orderformcategory",
                    join_on_collection="orderformcategory",
                    join_on_attribute="id",
                    alias_name="orderformcategory",
                ),
                ReportJoin(
                    from_object_name="orderformcategory",
                    from_property_name="worksection",
                    join_on_collection="worksection",
                    join_on_attribute="id",
                    alias_name="worksection",
                ),
            ],
            stage=StageGrouping(
                label=AttributeBucket(bucket_name="columns", attribute_name="stage"),
                summary=ReportComputation(
                    expression="sum(row['cost'] for row in rows)", unit_id="$"
                ),
            ),
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
async def test_given_report_definition(snapshot):
    datasheet_fixture = DatasheetInstanceFactory.build(datasheet_seed)
    project_fixture = ProjectInstanceFactory.build(
        project_seed,
        default_datasheet_id=datasheet_fixture.datasheet.id,
        datasheet_def_id=datasheet_fixture.datasheet_definition.id,
    )
    report_definition = make_general_report(project_fixture.project_definition.id)

    datasheet_definition_service = StrictInterfaceSetup(DatasheetDefinitionService)
    project_definition_service = StrictInterfaceSetup(ProjectDefinitionService)
    datasheet_definition_element_service = StrictInterfaceSetup(
        DatasheetDefinitionElementService
    )
    label_collection_service = StrictInterfaceSetup(LabelCollectionService)
    label_service = StrictInterfaceSetup(LabelService)
    formula_plucker = StrictInterfaceSetup(Plucker)

    project_definition_service.setup(
        lambda x: x.find_by_id(report_definition.project_def_id),
        returns_async=project_fixture.project_definition,
    )

    datasheet_def_id = datasheet_fixture.datasheet_definition.id

    datasheet_definition_service.setup(
        lambda x: x.find_by_id(datasheet_def_id),
        returns_async=datasheet_fixture.datasheet_definition,
    )

    datasheet_definition_element_service.setup(
        lambda x: x.find_by(
            DatasheetDefinitionElementFilter(datasheet_def_id=datasheet_def_id)
        ),
        returns_async=datasheet_fixture.datasheet_definition_elements,
    )

    label_collection_service.setup(
        lambda x: x.find_by(
            LabelCollectionFilter(datasheet_definition_id=datasheet_def_id)
        ),
        returns_async=datasheet_fixture.label_collections,
    )

    for label_collection in datasheet_fixture.label_collections:
        label_service.setup(
            lambda x: x.find_by(LabelFilter(label_collection_id=label_collection.id)),
            returns_async=[
                label
                for label in datasheet_fixture.labels
                if label.label_collection_id == label_collection.id
            ],
        )

    formula_plucker.setup(
        lambda x: x.plucks(lambda x: callable(x), lambda x: True),
        returns_async=project_fixture.formulas,
        compare_method=compare_per_arg,
    )

    report_linking = ReportRowCacheBuilder(
        datasheet_definition_service.object,
        project_definition_service.object,
        datasheet_definition_element_service.object,
        label_collection_service.object,
        label_service.object,
        formula_plucker.object,
    )

    report_buckets = await report_linking.refresh_cache(report_definition)
    snapshot.assert_match(dump_snapshot(report_buckets), "report_linking_test.json")


@pytest.mark.asyncio
async def test_given_row_cache_should_produce_correct_report():
    datasheet_fixture = DatasheetInstanceFactory.build(datasheet_seed)
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
            "formula": {
                "attached_to_type_id": UUID("37adfdd5-6143-9446-66fe-23b183399b25"),
                "expression": "fieldB*fieldA",
                "name": "formulaA",
            },
            "orderformcategory": {
                "id": UUID("444ea1f0-5338-5998-265d-1700d4327f51"),
                "name": "orderformcategory_label_0",
                "order_index": 0,
                "worksection": UUID("407be730-a7a7-9d39-183f-85a1b8017b47"),
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
                "datasheet_element": UUID("9edcbbf4-3696-80e9-59b5-aa8c5f94958b"),
                "formula": UUID("f1f1e0ff-2344-48bc-e757-8c9dcd3c671e"),
                "id": UUID("6fce3c97-2660-2ad4-9f6f-4c4921c8c59b"),
                "name": "substage_label_0",
                "order_index": 0,
                "orderformcategory": UUID("444ea1f0-5338-5998-265d-1700d4327f51"),
                "quantity": "0",
                "special_condition": True,
                "stage": UUID("68e30dbc-7508-6e56-8a1e-59ee389483d9"),
            },
            "worksection": {
                "id": UUID("407be730-a7a7-9d39-183f-85a1b8017b47"),
                "name": "worksection_label_0",
                "order_index": 0,
            },
        }
    ]

    report_def_row_cache = StrictInterfaceSetup(ObjectStorage)
    report_storage = StrictInterfaceSetup(ObjectStorage)
    unit_instance_storage = StrictInterfaceSetup(ObjectStorage)
    datasheet_element_plucker = StrictInterfaceSetup(Plucker)
    expression_evaluator = StrictInterfaceSetup(ExpressionEvaluator)
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

    unit_instance_storage.setup(
        lambda x: x.load(UnitInstanceCacheKey(project_id=project_fixture.project.id)),
        returns_async=project_fixture.unit_instances,
    )

    report_storage.setup(
        lambda x: x.load(
            ReportKey(
                project_id=project_fixture.project.id,
                report_definition_id=report_definition.id,
            )
        ),
        invoke=raise_async(RessourceNotFound()),
    )

    missing_element_ids = {
        report_definition.structure.datasheet_attribute.get(report_row_cache)
        for report_row_cache in report_rows_cache
    }

    datasheet_element_plucker.setup(
        lambda x: x.pluck_subressources(
            DatasheetElementFilter(
                datasheet_id=datasheet_fixture.datasheet.id,
                child_element_reference=zero_uuid(),
            ),
            lambda y: True,
            missing_element_ids,
        ),
        returns_async=[
            datasheet_element
            for datasheet_element in datasheet_fixture.datasheet_elements
            if datasheet_element.element_def_id in missing_element_ids
        ],
        compare_method=compare_per_arg,
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
        report_def_row_cache.object,
        report_storage.object,
        unit_instance_storage.object,
        datasheet_element_plucker.object,
        expression_evaluator.object,
        clock,
    )

    report_rows = await report_linking.link_report(
        report_definition, project_fixture.project
    )

    expected_rows = Report(
        stages=[
            ReportGroup(
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
