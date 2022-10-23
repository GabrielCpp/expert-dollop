from expert_dollup.core.domains import *
from ..fake_db_helpers import FakeDb
from .domains import *


class SimpleDatasheetDef:
    def __call__(self, db: FakeDb) -> None:
        project_definition = ProjectDefinitionFactory()
        db.add(project_definition)
        db.add(
            AggregateCollectionFactory(
                name="datasheet",
                is_abstract=True,
                attributes_schema={
                    "price": AggregateAttributeSchema(
                        name="price", details=DecimalFieldConfig()
                    ),
                    "conversion_factor": AggregateAttributeSchema(
                        name="conversion_factor", details=DecimalFieldConfig()
                    ),
                    "lost": AggregateAttributeSchema(
                        name="lost", details=DecimalFieldConfig()
                    ),
                },
            )
        )
        db.add(
            AggregateFactory(
                project_definition_id=project_definition.id,
                unit_id="cube_meter",
                is_collection=False,
                ordinal=0,
                name="concrete_mpa",
                attributes={
                    "price": AggregateAttribute(is_readonly=False, value=148.0),
                    "conversion_factor": AggregateAttribute(
                        is_readonly=False, value=35.328
                    ),
                    "lost": AggregateAttribute(is_readonly=False, value=0.05),
                },
                tags=[],
            ),
            AggregateFactory(
                project_definition_id=project_definition.id,
                unit_id="cube_meter",
                is_collection=False,
                ordinal=1,
                name="concrete_mpa_air",
                attributes={
                    "price": AggregateAttribute(is_readonly=False, value=148.0),
                    "conversion_factor": AggregateAttribute(
                        is_readonly=False, value=35.328
                    ),
                    "lost": AggregateAttribute(is_readonly=False, value=0.05),
                },
                tags=[],
            ),
            AggregateFactory(
                project_definition_id=project_definition.id,
                unit_id="square_foot",
                is_collection=True,
                ordinal=2,
                name="tile_wall_ceramic",
                default_properties={
                    "price": AggregateAttribute(is_readonly=False, value=4.0),
                    "conversion_factor": AggregateAttribute(
                        is_readonly=False, value=1.0
                    ),
                    "lost": AggregateAttribute(is_readonly=False, value=0.05),
                },
                tags=[],
            ),
        )

        order_form_category = AggregateCollectionFactory(
            project_definition_id=project_definition.id,
            name="orderformcategory",
        )

        db.add(order_form_category)

        product_category = AggregateCollectionFactory(
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
