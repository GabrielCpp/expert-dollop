from decimal import Decimal
from expert_dollup.core.domains import *
from ..fake_db_helpers import FakeDb
from .domains import *


class MiniDatasheet:
    def __call__(self, db: FakeDb) -> None:
        project_definition = db.add(
            ProjectDefinitionFactory(
                name=f"datasheet_definition_a",
            )
        )

        collection = db.add(
            AggregateCollectionFactory(
                project_definition_id=project_definition.id,
                name="abstract_product",
                attributes_schema={
                    "conversion_factor": DecimalFieldConfig(),
                    "lost": DecimalFieldConfig(),
                },
            )
        )

        aggregate_a = AggregateFactory(
            collection_id=collection.id,
            ordinal=0,
            name="aggregate_a",
        )

        aggregate_b = AggregateFactory(
            collection_id=collection.id,
            ordinal=1,
            name="aggregate_b",
        )

        db.add(
            Aggregate(
                unit_id="inch",
                is_collection=False,
                project_definition_id=project_definition.id,
                ordinal=0,
                name="single_element",
                attributes={
                    "conversion_factor": AggregateAttribute(
                        name="conversion_factor", is_readonly=True, value=Decimal(2)
                    ),
                    "lost": AggregateAttribute(
                        name="lost", is_readonly=False, value=Decimal(1)
                    ),
                },
                tags=[str(aggregate_a.id)],
            )
        )

        db.add(
            Aggregate(
                unit_id="inch",
                is_collection=True,
                project_definition_id=project_definition.id,
                ordinal=0,
                name="collection_element",
                attributes={
                    "conversion_factor": AggregateAttribute(
                        name="conversion_factor", is_readonly=True, value=Decimal("1.5")
                    ),
                    "lost": AggregateAttribute(
                        name="lost", is_readonly=False, value=Decimal(0)
                    ),
                },
                tags=[aggregate_b.id],
            )
        )

        return db
