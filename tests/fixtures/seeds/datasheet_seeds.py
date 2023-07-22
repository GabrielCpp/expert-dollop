from decimal import Decimal
from expert_dollup.core.domains import *
from ..factories.datasheet_factory import (
    DatasheetSeed,
    ElementSeed,
    AggregateCollectionSeed,
)


def make_base_datasheet(project_seed):
    datasheet_seed = DatasheetSeed(
        attributes={"price": Decimal, "factor": Decimal},
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
                tags=["productcategory_label_2"], unit_id="m", is_extendable=True
            ),
        },
        collection_seeds={
            "datasheetelement_binding": AggregateCollectionSeed(
                label_count=10,
                schemas={
                    "formula": NodeReferenceConfig(node_type=NodeType.FORMULA),
                    "special_condition": bool,
                    "quantity": Decimal,
                    "stage": AggregateReferenceConfig("stage"),
                    "orderformcategory": AggregateReferenceConfig("orderformcategory"),
                    "datasheet_element": AggregateReferenceConfig("datasheet"),
                },
            ),
            "substage": AggregateCollectionSeed(
                label_count=10,
                schemas={
                    "formula": NodeReferenceConfig(node_type=NodeType.FORMULA),
                    "special_condition": bool,
                    "quantity": Decimal,
                    "stage": AggregateReferenceConfig("stage"),
                    "orderformcategory": AggregateReferenceConfig("orderformcategory"),
                    "datasheet_element": AggregateReferenceConfig("datasheet"),
                },
            ),
            "stage": AggregateCollectionSeed(
                label_count=5,
                schemas={
                    "localisation": str,
                    "associated_global_section": str,
                    "compile_in_one": bool,
                    "floor": AggregateReferenceConfig("floor"),
                },
            ),
            "orderformcategory": AggregateCollectionSeed(
                label_count=3,
                schemas={"worksection": AggregateReferenceConfig("worksection")},
            ),
            "worksection": AggregateCollectionSeed(label_count=3),
            "productcategory": AggregateCollectionSeed(label_count=3),
            "floor": AggregateCollectionSeed(label_count=3),
            "datasheet": AggregateCollectionSeed(label_count=3),
        },
        formulas=project_seed.formulas,
    )

    return datasheet_seed
