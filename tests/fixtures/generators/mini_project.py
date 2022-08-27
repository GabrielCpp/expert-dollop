from ..fake_db_helpers import FakeDb
from ..factories import FieldConfigFactory
from expert_dollup.core.domains import *
from ..factories_domain import *


class MiniProject:
    def __init__(self):
        self.field_config_factory = FieldConfigFactory()

    def __call__(self, db: FakeDb) -> None:
        project_definition = db.add(ProjectDefinitionFactory())
        root = db.add(
            ProjectDefinitionNodeFactory(
                name="root",
                project_definition_id=project_definition.id,
                path=[],
                is_collection=False,
                instanciate_by_default=True,
                order_index=0,
                translations=TranslationConfig(
                    help_text_name="root_help_text", label="root"
                ),
            )
        )

        name_map = {
            IntFieldConfig: "quantity",
            StringFieldConfig: "item_name",
            DecimalFieldConfig: "price",
            BoolFieldConfig: "is_confirmed",
            StaticChoiceFieldConfig: "item_size",
        }

        parents = [root.id]
        for index, config_type in enumerate(
            self.field_config_factory.field_config_types
        ):
            name = name_map[config_type]
            field_details = self.field_config_factory.build(name, index, config_type)
            db.add(
                ProjectDefinitionNodeFactory(
                    name=name,
                    project_definition_id=project_definition.id,
                    path=parents,
                    is_collection=False,
                    instanciate_by_default=True,
                    order_index=index,
                    field_details=field_details,
                )
            )

        index = len(name_map)
        name = "taxes"
        field_details = self.field_config_factory.build(name, index, config_type)
        db.add(
            ProjectDefinitionNodeFactory(
                name=name,
                project_definition_id=project_definition.id,
                path=parents,
                is_collection=True,
                instanciate_by_default=True,
                order_index=index,
                field_details=field_details,
            )
        )
