from pydantic import BaseModel, parse_file_as
from typing import List, Dict, Any
from pydantic.tools import parse_file_as
import pytest
from uuid import UUID
from expert_dollup.core.object_storage import ObjectStorage
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


class ReportDict(BaseModel):
    __root__: List[Dict[str, Dict[str, Any]]]


"""
CREATE FUNCTION get_room_floor(
	project_id BINARY(16),
    root_section_id BINARY(16),
	floor_name VARCHAR(64) CHARSET UTF8 COLLATE utf8_unicode_ci,
    locale VARCHAR(5) CHARSET UTF8 COLLATE utf8_unicode_ci
)
RETURNS VARCHAR(64) CHARSET UTF8 COLLATE utf8_unicode_ci
DETERMINISTIC
BEGIN
	IF floor_name = 'pmctp ' THEN
		RETURN (
			SELECT floortranslation.description
			FROM project_container_definition AS field_def
			INNER JOIN project_container AS field
			ON 
				field.project_id = project_id AND
				field.root_section_id = root_section_id AND
				field.type_id = field_def.id AND
                field.level = field_level()
			INNER JOIN floortranslation
			ON 
				floortranslation.owner_id = (
					CASE get_element_dec_value( field.value )
                    -- Quatrième
                    WHEN 5 THEN 11
                    -- Cinquième
                    WHEN 6 THEN 12
                    -- Sixième
                    WHEN 7 THEN 13
                    -- Garage
                    WHEN 8 THEN 6
					ELSE get_element_dec_value( field.value )
					END
				) AND
				floortranslation.locale = locale
			WHERE field_def.name = 'pmccu_choice'
        );
    END IF;
    
    RETURN floor_name;
END//

CREATE FUNCTION get_room_floor_index(
	project_id BINARY(16),
    root_section_id BINARY(16),
	floor_name VARCHAR(64) CHARSET UTF8 COLLATE utf8_unicode_ci
)
RETURNS VARCHAR(64) CHARSET UTF8 COLLATE utf8_unicode_ci
DETERMINISTIC
BEGIN
	IF floor_name = 'pmctp ' THEN
		RETURN (
			SELECT floor.order_index
			FROM project_container_definition AS field_def
			INNER JOIN project_container AS field
			ON 
				field.project_id = project_id AND
				field.root_section_id = root_section_id AND
				field.type_id = field_def.id AND
        field.level = field_level()
			INNER JOIN floor
			ON 
				floor.id = (
					CASE get_element_dec_value( field.value )
                    -- Quatrième
                    WHEN 5 THEN 11
                    -- Cinquième
                    WHEN 6 THEN 12
                    -- Sixième
                    WHEN 7 THEN 13
                    -- Garage
                    WHEN 8 THEN 6
					ELSE get_element_dec_value( field.value )
					END
				)
			WHERE field_def.name = 'pmccu_choice'
        );
    END IF;
    
    RETURN NULL;
END//

"""
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
                    expression="row['floor']['translation']",
                ),
                ReportColumn(
                    name="substage_description",
                    expression="row['substage']['translation']",
                ),
                ReportColumn(
                    name="abstract_product_description",
                    expression="row['abstractproduct']['translation']",
                ),
                ReportColumn(
                    name="cost_per_unit",
                    expression="format_currency(row['datasheet_element']['price'], 2, 'truncate')",
                ),
                ReportColumn(
                    name="result",
                    expression="sum(row['formula']['result'] * row['columns']['post_transform_factor'] for row in rows)",
                ),
                ReportColumn(
                    name="cost",
                    expression="format_currency( round_number( sum(row['formula']['result'] * row['columns']['post_transform_factor'] for row in rows), 2, 'truncate') * row['datasheet_element']['price'], 2, 'truncate')",
                ),
                ReportColumn(
                    name="order_form_category_description",
                    expression="row['orderformcategory']['translation']",
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
            stage_attribute=AttributeBucket(
                bucket_name="columns", attribute_name="stage"
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

    report_linking = ReportRowCacheBuilder(
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

    report_rows_cache = (
        parse_file_as(
            ReportDict,
            "tests/units/core/units/snapshots/report_linking_test/test_given_report_definition/report_linking_test.json",
        ),
    )[0].__root__

    report_def_row_cache = StrictInterfaceSetup(
        ObjectStorage[ReportRowsCache, ReportRowKey]
    )
    report_row_service = StrictInterfaceSetup(ReportRowService)
    formula_instance_plucker = StrictInterfaceSetup(Plucker)
    datasheet_element_plucker = StrictInterfaceSetup(Plucker)

    report_def_row_cache.setup(
        lambda x: x.find_by(
            ReportDefinitionRowCacheFilter(report_def_id=report_definition.id)
        ),
        returns_async=report_rows_cache,
    )

    formula_instance_plucker.setup(
        lambda x: x.pluck_subressources(lambda y: True, lambda y: True, lambda y: True),
        returns_async=project_fixture.formula_instances,
        compare_method=compare_per_arg,
    )

    report_row_service.setup(
        lambda x: x.find_by(ReportRowFilter(project_id=project_fixture.project.id)),
        returns_async=[],
    )

    missing_element_ids = {
        UUID(report_definition.structure.datasheet_attribute.get(report_row_cache))
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

    report_linking = ReportLinking(
        report_def_row_cache.object,
        report_row_service.object,
        formula_instance_plucker.object,
        datasheet_element_plucker.object,
        ExpressionEvaluator(),
    )

    report_rows = await report_linking.link_report(
        report_definition, project_fixture.project
    )

    dump_to_file(report_rows)
