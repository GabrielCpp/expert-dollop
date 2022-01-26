from decimal import Decimal
from expert_dollup.core.domains import *
from ..factories.datasheet_factory import DatasheetSeed, ElementSeed, CollectionSeed


def make_base_datasheet(project_seed):
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
            "datasheetelement_binding": CollectionSeed(
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
                label_count=3,
                schemas={"worksection": CollectionAggregate("worksection")},
            ),
            "worksection": CollectionSeed(label_count=3),
            "productcategory": CollectionSeed(label_count=3),
            "floor": CollectionSeed(label_count=3),
        },
        formulas=project_seed.formulas,
    )

    return datasheet_seed