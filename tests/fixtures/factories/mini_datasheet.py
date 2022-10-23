from decimal import Decimal
from expert_dollup.core.domains import *
from expert_dollup.core.utils import by_names
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
                is_abstract=True,
                name="abstract_product",
                attributes_schema=by_names(
                    [
                        AggregateAttributeSchemaFactory(
                            name="conversion_factor",
                            details=DecimalFieldConfigFactory(),
                        ),
                        AggregateAttributeSchemaFactory(
                            name="lost",
                            details=DecimalFieldConfigFactory(),
                        ),
                    ]
                ),
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
            AggregateFactory(
                is_extendable=False,
                project_definition_id=project_definition.id,
                ordinal=0,
                collection_id=collection.id,
                name="single_element",
                attributes=by_names(
                    [
                        AggregateAttributeFactory(
                            name="conversion_factor", is_readonly=True, value=Decimal(2)
                        ),
                        AggregateAttributeFactory(
                            name="lost", is_readonly=False, value=Decimal(1)
                        ),
                    ]
                ),
            )
        )

        db.add(
            AggregateFactory(
                is_extendable=True,
                project_definition_id=project_definition.id,
                ordinal=0,
                collection_id=collection.id,
                name="collection_element",
                attributes=by_names(
                    [
                        AggregateAttributeFactory(
                            name="conversion_factor",
                            is_readonly=True,
                            value=Decimal("1.5"),
                        ),
                        AggregateAttributeFactory(
                            name="lost", is_readonly=False, value=Decimal(0)
                        ),
                    ]
                ),
            )
        )

        return db
