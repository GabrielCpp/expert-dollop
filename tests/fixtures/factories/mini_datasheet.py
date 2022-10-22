from decimal import Decimal
from expert_dollup.core.domains import *
from ..fake_db_helpers import FakeDb
from ..factories_domain import *


class MiniDatasheet:
    def __call__(self, db: FakeDb) -> None:
        project_definition = db.add(
            ProjectDefinitionFactory(
                name=f"datasheet_definition_a",
                properties={
                    "conversion_factor": ElementPropertySchema(
                        value_validator={"type": "number"}
                    ),
                    "lost": ElementPropertySchema(value_validator={"type": "number"}),
                },
            )
        )

        aggregate_a = AggregateFactory(
            ordinal=0,
            name="aggregate_a",
        )

        aggregate_b = AggregateFactory(
            ordinal=1,
            name="aggregate_b",
        )

        aggregation = db.add(
            AggregationFactory(
                project_definition_id=project_definition.id,
                name="abstract_product",
                aggregates=[aggregate_a, aggregate_b],
            )
        )

        db.add(
            DatasheetDefinitionElementFactory(
                unit_id="inch",
                is_collection=False,
                project_definition_id=project_definition.id,
                ordinal=0,
                name="single_element",
                default_properties={
                    "conversion_factor": DatasheetDefinitionElementProperty(
                        is_readonly=True, value=Decimal(2)
                    ),
                    "lost": DatasheetDefinitionElementProperty(
                        is_readonly=False, value=Decimal(1)
                    ),
                },
                tags=[str(aggregate_a.id)],
            )
        )

        db.add(
            DatasheetDefinitionElementFactory(
                unit_id="inch",
                is_collection=True,
                project_definition_id=project_definition.id,
                ordinal=0,
                name="collection_element",
                default_properties={
                    "conversion_factor": DatasheetDefinitionElementProperty(
                        is_readonly=True, value=Decimal("1.5")
                    ),
                    "lost": DatasheetDefinitionElementProperty(
                        is_readonly=False, value=Decimal(0)
                    ),
                },
                tags=[aggregate_b.id],
            )
        )

        return db
