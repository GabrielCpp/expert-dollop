from uuid import uuid4, UUID
from datetime import timezone
from faker import Faker
from typing import List
from pydantic import BaseModel
from expert_dollup.core.domains import *
from ..fake_db_helpers import FakeExpertDollupDb as Tables
from ..factories import FieldConfigFactory


class SimpleDatasheetDef:
    def __init__(self):
        self.tables = Tables()
        self.fake = Faker()
        self.fake.seed_instance(seed=1)

    def generate(self):
        datasheet_definition = DatasheetDefinition(
            id=uuid4(),
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
        )
        self.tables.datasheet_definitions.append(datasheet_definition)

        self.tables.datasheet_definition_elements.extend(
            [
                DatasheetDefinitionElement(
                    id=uuid4(),
                    datasheet_def_id=datasheet_definition.id,
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
                    datasheet_def_id=datasheet_definition.id,
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
                    datasheet_def_id=datasheet_definition.id,
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
            ]
        )

        order_form_category = LabelCollection(
            id=uuid4(),
            datasheet_definition_id=datasheet_definition.id,
            name="orderformcategory",
        )

        self.tables.label_collections.append(order_form_category)

        product_category = LabelCollection(
            id=uuid4(),
            datasheet_definition_id=datasheet_definition.id,
            name="_".join(self.fake.words()),
        )

        self.tables.label_collections.append(product_category)

        self.tables.labels.extend(
            [
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
                Label(
                    id=uuid4(), order_index=0, label_collection_id=product_category.id
                ),
                Label(
                    id=uuid4(), order_index=1, label_collection_id=product_category.id
                ),
            ]
        )

        for label in self.tables.labels:
            words = self.fake.words()
            self.tables.translations.append(
                Translation(
                    id=uuid4(),
                    ressource_id=datasheet_definition.id,
                    locale="fr",
                    name="_".join(words),
                    scope=label.label_collection_id,
                    value=" ".join(words),
                    creation_date_utc=self.fake.date_time(),
                )
            )

            self.tables.translations.append(
                Translation(
                    id=uuid4(),
                    ressource_id=datasheet_definition.id,
                    locale="en",
                    name="_".join(words),
                    scope=label.label_collection_id,
                    value=" ".join(words),
                    creation_date_utc=self.fake.date_time(),
                )
            )

        return self

    @property
    def model(self) -> Tables:
        return self.tables