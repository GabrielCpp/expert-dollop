import pytest
from tests.fixtures.mock_interface_utils import StrictInterfaceSetup
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
            tags=["wood"],
            unit_id="m",
        )
    },
    collection_seeds={
        "collection_a": CollectionSeed(
            label_count=5,
            properties={
                "name": str,
            },
            aggregates={"datasheet_items": 0},
        )
    },
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
            initial_selection=ReportInitialSelection(
                from_object_name="substage",
                from_property_name="formula",
                alias_name="project_report_formula",
                distinct=True,
            ),
            joins_cache=[
                ReportJoin(
                    from_object_name="",
                    from_property_name="",
                    to_object_name="",
                    to_property_name="",
                    alias_name="",
                )
            ],
            joins=[
                ReportJoin(
                    from_object_name="",
                    from_property_name="",
                    to_object_name="",
                    to_property_name="",
                    alias_name="",
                )
            ],
        ),
        group_by=[
            "stage",
            "substage_description",
            "abstract_product_description",
            "order_form_category_description",
        ],
        order_by=["stage_order", "substage_order"],
    )

    report_definition_service = StrictInterfaceSetup(ReportDefinitionService)
    label_collection_service = StrictInterfaceSetup(LabelCollectionService)
    label_service = StrictInterfaceSetup(LabelService)
    label_plucker = StrictInterfaceSetup(Plucker)
    report_linking = ReportLinking(
        report_definition_service.object,
        label_collection_service.object,
        label_service.object,
        label_plucker.object,
    )
    # await report_linking.refresh_cache(report_definition)
    # report_linking.link_report(report_definition, project_fixture.project, "fr_CA")
