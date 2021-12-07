from uuid import uuid4, UUID
from faker import Faker
from expert_dollup.core.domains import *
from ..fake_db_helpers import FakeDb


class MiniDatasheet:
    def __init__(self):
        self.db = FakeDb()
        self.fake = Faker()
        self.fake.seed_instance(seed=1)

    def generate(self):
        datasheet_definition = DatasheetDefinition(
            id=uuid4(),
            name=f"datasheet_definition_a",
            properties={
                "conversion_factor": ElementPropertySchema(
                    value_validator={"type": "number"}
                ),
                "lost": ElementPropertySchema(value_validator={"type": "number"}),
            },
        )
        self.db.add(datasheet_definition)

        label_collection = LabelCollection(
            id=uuid4(),
            datasheet_definition_id=datasheet_definition.id,
            name="abstract_product",
        )
        self.db.add(label_collection)

        label_a = Label(
            id=uuid4(), label_collection_id=label_collection.id, order_index=0
        )
        self.db.add(label_a)

        label_b = Label(
            id=uuid4(), label_collection_id=label_collection.id, order_index=0
        )
        self.db.add(label_b)

        datasheet_definition_element_single = DatasheetDefinitionElement(
            id=uuid4(),
            unit_id="inch",
            is_collection=False,
            datasheet_def_id=datasheet_definition.id,
            order_index=0,
            name="single_element",
            default_properties={
                "conversion_factor": DatasheetDefinitionElementProperty(
                    is_readonly=True, value=2
                ),
                "lost": DatasheetDefinitionElementProperty(is_readonly=False, value=1),
            },
            tags=[str(label_a.id)],
            creation_date_utc=self.fake.date_time(),
        )
        self.db.add(datasheet_definition_element_single)

        datasheet_definition_element_collection = DatasheetDefinitionElement(
            id=uuid4(),
            unit_id="inch",
            is_collection=True,
            datasheet_def_id=datasheet_definition.id,
            order_index=0,
            name="collection_element",
            default_properties={
                "conversion_factor": DatasheetDefinitionElementProperty(
                    is_readonly=True, value=1.5
                ),
                "lost": DatasheetDefinitionElementProperty(is_readonly=False, value=0),
            },
            tags=[str(label_b.id)],
            creation_date_utc=self.fake.date_time(),
        )
        self.db.add(datasheet_definition_element_collection)

        return self

    @property
    def model(self) -> FakeDb:
        return self.db
