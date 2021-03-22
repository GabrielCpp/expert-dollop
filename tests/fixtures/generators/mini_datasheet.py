from uuid import uuid4, UUID
from faker import Faker
from expert_dollup.core.domains import *
from ..fake_db_helpers import FakeExpertDollupDb as Tables


class MiniDatasheet:
    def __init__(self):
        self.tables = Tables()
        self.fake = Faker()
        self.fake.seed_instance(seed=1)

    def generate(self):
        datasheet_definition = DatasheetDefinition(
            id=uuid4(),
            name=f"datasheet_definition_a",
            element_properties_schema={
                "conversion_factor": {"type": "number"},
                "lost": {"type": "number"},
            },
        )
        self.tables.datasheet_definitions.append(datasheet_definition)

        label_collection = LabelCollection(
            id=uuid4(),
            datasheet_definition_id=datasheet_definition.id,
            name="abstract_product",
        )
        self.tables.label_collections.append(label_collection)

        label_a = Label(
            id=uuid4(), label_collection_id=label_collection.id, order_index=0
        )
        self.tables.labels.append(label_a)

        label_b = Label(
            id=uuid4(), label_collection_id=label_collection.id, order_index=0
        )
        self.tables.labels.append(label_b)

        datasheet_definition_element_single = DatasheetDefinitionElement(
            id=uuid4(),
            unit_id=uuid4(),
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
        self.tables.datasheet_definition_elements.append(
            datasheet_definition_element_single
        )

        datasheet_definition_element_collection = DatasheetDefinitionElement(
            id=uuid4(),
            unit_id=uuid4(),
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
        self.tables.datasheet_definition_elements.append(
            datasheet_definition_element_collection
        )

        return self

    @property
    def model(self) -> Tables:
        return self.tables
