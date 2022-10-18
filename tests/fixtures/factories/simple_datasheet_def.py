from expert_dollup.core.domains import *
from ..fake_db_helpers import FakeDb
from ..factories_domain import *


class SimpleDatasheetDef:
    def __call__(self, db: FakeDb) -> None:
        project_definition = ProjectDefinitionFactory(
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
            }
        )
        db.add(project_definition)
        db.add(
            DatasheetDefinitionElementFactory(
                project_definition_id=project_definition.id,
                unit_id="cube_meter",
                is_collection=False,
                ordinal=0,
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
            ),
            DatasheetDefinitionElementFactory(
                project_definition_id=project_definition.id,
                unit_id="cube_meter",
                is_collection=False,
                ordinal=1,
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
            ),
            DatasheetDefinitionElement(
                project_definition_id=project_definition.id,
                unit_id="square_foot",
                is_collection=True,
                ordinal=2,
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
            ),
        )

        order_form_category = LabelCollectionFactory(
            project_definition_id=project_definition.id,
            name="orderformcategory",
        )

        db.add(order_form_category)

        product_category = LabelCollectionFactory(
            project_definition_id=project_definition.id
        )

        db.add(product_category)

        db.add(
            LabelFactory(
                id=uuid4(),
                ordinal=0,
                label_collection_id=order_form_category.id,
            ),
            LabelFactory(
                id=uuid4(),
                ordinal=1,
                label_collection_id=order_form_category.id,
            ),
            LabelFactory(
                id=uuid4(), ordinal=0, label_collection_id=product_category.id
            ),
            LabelFactory(
                id=uuid4(), ordinal=1, label_collection_id=product_category.id
            ),
        )

        for label in db.all(Label):
            db.add(
                TranslationFactory(
                    ressource_id=project_definition.id,
                    locale="fr-CA",
                    name="project_definition_fr_ca_label",
                    scope=label.label_collection_id,
                    value="project_definition_fr_ca_label",
                )
            )

            db.add(
                TranslationFactory(
                    ressource_id=project_definition.id,
                    locale="en-US",
                    name="project_definition_en_us_label",
                    scope=label.label_collection_id,
                    value="project_definition_en_us_label",
                )
            )
