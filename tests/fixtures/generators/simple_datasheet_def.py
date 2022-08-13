from uuid import uuid4
from faker import Faker
from expert_dollup.core.domains import *
from ..fake_db_helpers import FakeDb
from ..factories_domain import *


class SimpleDatasheetDef:
    def __init__(self):
        self.db = FakeDb()
        self.fake = Faker()
        self.fake.seed_instance(seed=1)

    def __call__(self):
        project_definition = ProjectDefinitionFactory(
            name="".join(self.fake.words()),
            properties={
                "price": ElementPropertySchema(
                    value_validator={
                        "type": "number",
                        "minimum": -100000,
                        "maximum": 100000,
                    }
                ),
                "conversion_factor": ElementPropertySchema(
                    value_validator={
                        "type": "number",
                        "minimum": -100000,
                        "maximum": 100000,
                    }
                ),
                "lost": ElementPropertySchema(
                    value_validator={
                        "type": "number",
                        "minimum": -100000,
                        "maximum": 100000,
                    }
                ),
            },
            creation_date_utc=self.fake.date_time(),
        )
        self.db.add(project_definition)
        self.db.add(
            DatasheetDefinitionElement(
                id=uuid4(),
                project_definition_id=project_definition.id,
                unit_id="cube_meter",
                is_collection=False,
                order_index=0,
                name="concrete_mpa",
                default_properties={
                    "price": DatasheetDefinitionElementProperty(
                        is_readonly=False, value=148.0
                    ),
                    "conversion_factor": DatasheetDefinitionElementProperty(
                        is_readonly=False, value=35.328
                    ),
                    "lost": DatasheetDefinitionElementProperty(
                        is_readonly=False, value=0.05
                    ),
                },
                tags=[],
                creation_date_utc=self.fake.date_time(),
            ),
            DatasheetDefinitionElement(
                id=uuid4(),
                project_definition_id=project_definition.id,
                unit_id="cube_meter",
                is_collection=False,
                order_index=1,
                name="concrete_mpa_air",
                default_properties={
                    "price": DatasheetDefinitionElementProperty(
                        is_readonly=False, value=148.0
                    ),
                    "conversion_factor": DatasheetDefinitionElementProperty(
                        is_readonly=False, value=35.328
                    ),
                    "lost": DatasheetDefinitionElementProperty(
                        is_readonly=False, value=0.05
                    ),
                },
                tags=[],
                creation_date_utc=self.fake.date_time(),
            ),
            DatasheetDefinitionElement(
                id=uuid4(),
                project_definition_id=project_definition.id,
                unit_id="square_foot",
                is_collection=True,
                order_index=2,
                name="tile_wall_ceramic",
                default_properties={
                    "price": DatasheetDefinitionElementProperty(
                        is_readonly=False, value=4.0
                    ),
                    "conversion_factor": DatasheetDefinitionElementProperty(
                        is_readonly=False, value=1.0
                    ),
                    "lost": DatasheetDefinitionElementProperty(
                        is_readonly=False, value=0.05
                    ),
                },
                tags=[],
                creation_date_utc=self.fake.date_time(),
            ),
        )

        order_form_category = LabelCollection(
            id=uuid4(),
            project_definition_id=project_definition.id,
            name="orderformcategory",
        )

        self.db.add(order_form_category)

        product_category = LabelCollection(
            id=uuid4(),
            project_definition_id=project_definition.id,
            name="_".join(self.fake.words()),
        )

        self.db.add(product_category)

        self.db.add(
            Label(
                id=uuid4(),
                order_index=0,
                label_collection_id=order_form_category.id,
            ),
            Label(
                id=uuid4(),
                order_index=1,
                label_collection_id=order_form_category.id,
            ),
            Label(id=uuid4(), order_index=0, label_collection_id=product_category.id),
            Label(id=uuid4(), order_index=1, label_collection_id=product_category.id),
        )

        for label in self.db.all(Label):
            words = self.fake.words()
            self.db.add(
                Translation(
                    id=uuid4(),
                    ressource_id=project_definition.id,
                    locale="fr-CA",
                    name="_".join(words),
                    scope=label.label_collection_id,
                    value=" ".join(words),
                    creation_date_utc=self.fake.date_time(),
                )
            )

            self.db.add(
                Translation(
                    id=uuid4(),
                    ressource_id=project_definition.id,
                    locale="en-US",
                    name="_".join(words),
                    scope=label.label_collection_id,
                    value=" ".join(words),
                    creation_date_utc=self.fake.date_time(),
                )
            )

        return self.db
