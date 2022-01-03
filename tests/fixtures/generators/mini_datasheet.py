from decimal import Decimal
from expert_dollup.core.domains import *
from ..fake_db_helpers import FakeDb, DbFixtureGenerator
from ..factories_domain import *


class MiniDatasheet(DbFixtureGenerator):
    def __init__(self):
        self._db = FakeDb()

    @property
    def db(self) -> FakeDb:
        return self._db

    def generate(self):
        datasheet_definition = self.db.add(
            DatasheetDefinitionFactory(
                name=f"datasheet_definition_a",
                properties={
                    "conversion_factor": ElementPropertySchema(
                        value_validator={"type": "number"}
                    ),
                    "lost": ElementPropertySchema(value_validator={"type": "number"}),
                },
            )
        )

        label_collection = self.db.add(
            LabelCollectionFactory(
                datasheet_definition_id=datasheet_definition.id,
                name="abstract_product",
            )
        )

        label_a = self.db.add(
            LabelFactory(
                label_collection_id=label_collection.id,
                order_index=0,
                name="label_a",
            )
        )

        label_b = self.db.add(
            LabelFactory(
                label_collection_id=label_collection.id,
                order_index=1,
                name="label_b",
            )
        )

        self.db.add(
            DatasheetDefinitionElementFactory(
                unit_id="inch",
                is_collection=False,
                datasheet_def_id=datasheet_definition.id,
                order_index=0,
                name="single_element",
                default_properties={
                    "conversion_factor": DatasheetDefinitionElementProperty(
                        is_readonly=True, value=Decimal(2)
                    ),
                    "lost": DatasheetDefinitionElementProperty(
                        is_readonly=False, value=Decimal(1)
                    ),
                },
                tags=[str(label_a.id)],
            )
        )

        self.db.add(
            DatasheetDefinitionElementFactory(
                unit_id="inch",
                is_collection=True,
                datasheet_def_id=datasheet_definition.id,
                order_index=0,
                name="collection_element",
                default_properties={
                    "conversion_factor": DatasheetDefinitionElementProperty(
                        is_readonly=True, value=Decimal("1.5")
                    ),
                    "lost": DatasheetDefinitionElementProperty(
                        is_readonly=False, value=Decimal(0)
                    ),
                },
                tags=[label_b.id],
            )
        )

        return self

    @property
    def model(self) -> FakeDb:
        return self.db
