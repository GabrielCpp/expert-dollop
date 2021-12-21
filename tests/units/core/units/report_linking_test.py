import pytest
from tests.fixtures.mock_interface_utils import (
    StrictInterfaceSetup,
    compare_per_arg,
)
from expert_dollup.app.dtos import *
from expert_dollup.core.units import *
from expert_dollup.core.domains import *
from expert_dollup.core.queries import *
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
    properties={"price": float, "factor": float},
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
                "quantity": float,
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


@pytest.mark.asyncio
async def test_given_report_definition():
    datasheet_fixture = DatasheetInstanceFactory.build(datasheet_seed)
    project_fixture = ProjectInstanceFactory.build(
        project_seed,
        default_datasheet_id=datasheet_fixture.datasheet.id,
        datasheet_def_id=datasheet_fixture.datasheet_definition.id,
    )
    report_definition = ReportDefinitionFactory(
        project_def_id=project_fixture.project_definition.id,
        name="general_report",
        columns=[
            ReportColumn(
                name="get_element_first_level_value( floor_description_join.value ) or floor_description",
                expression="stage",
            ),
            ReportColumn(
                name="substage_description",
                expression="substage_description",
            ),
            ReportColumn(
                name="abstract_product_description",
                expression="view_joined_datasheet.name",
            ),
            ReportColumn(
                name="cost_per_unit",
                expression="CONCAT( TRUNCATE( view_joined_datasheet.price, 2 ), ' $' )",
            ),
            ReportColumn(
                name="cost",
                expression="CONCAT( TRUNCATE( TRUNCATE( SUM( get_element_dec_value( project_formula.value ) * post_transform_factor ), 2)  * view_joined_datasheet.price, 2), ' $' )",
            ),
            ReportColumn(
                name="order_form_category_description",
                expression="order_form_category_description",
            ),
        ],
        structure=ReportStructure(
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
        ),
        group_by=[
            "stage",
            "substage_description",
            "abstract_product_description",
            "order_form_category_description",
        ],
        order_by=["stage.order", "substage.order"],
    )

    datasheet_definition_service = StrictInterfaceSetup(DatasheetDefinitionService)
    project_definition_service = StrictInterfaceSetup(ProjectDefinitionService)
    datasheet_definition_element_service = StrictInterfaceSetup(
        DatasheetDefinitionElementService
    )
    report_definition_service = StrictInterfaceSetup(ReportDefinitionService)
    label_collection_service = StrictInterfaceSetup(LabelCollectionService)
    label_service = StrictInterfaceSetup(LabelService)
    translation_plucker = StrictInterfaceSetup(Plucker)
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

    translation_plucker.setup(
        lambda x: x.plucks(lambda x: callable(x), lambda x: True),
        returns_async=datasheet_fixture.translations,
        compare_method=compare_per_arg,
    )

    formula_plucker.setup(
        lambda x: x.plucks(lambda x: callable(x), lambda x: True),
        returns_async=project_fixture.formulas,
        compare_method=compare_per_arg,
    )

    report_linking = ReportLinking(
        datasheet_definition_service.object,
        project_definition_service.object,
        datasheet_definition_element_service.object,
        report_definition_service.object,
        label_collection_service.object,
        label_service.object,
        translation_plucker.object,
        formula_plucker.object,
    )

    report_buckets = await report_linking.refresh_cache(report_definition)
    dump_to_file(report_buckets)
    # report_linking.link_report(report_definition, project_fixture.project, "fr_CA")
