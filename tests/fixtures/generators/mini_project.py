from ..fake_db_helpers import FakeDb, DbFixtureGenerator
from ..factories import FieldConfigFactory
from expert_dollup.core.domains import *
from ..factories_domain import *


class MiniProject(DbFixtureGenerator):
    def __init__(self):
        self._db = FakeDb()
        self.field_config_factory = FieldConfigFactory()

    @property
    def db(self) -> FakeDb:
        return self._db

    def generate(self):
        project_definition = self.db.add(ProjectDefinitionFactory())
        root = self.db.add(
            ProjectDefinitionNodeFactory(
                name="root",
                project_definition_id=project_definition.id,
                path=[],
                is_collection=False,
                instanciate_by_default=True,
                order_index=0,
                config=NodeConfig(
                    translations=TranslationConfig(
                        help_text_name="root_help_text", label="root"
                    ),
                ),
                default_value=None,
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
            value = self.field_config_factory.build_value(config_type)
            config = self.field_config_factory.build_config(name, index, config_type)
            self.db.add(
                ProjectDefinitionNodeFactory(
                    name=name,
                    project_definition_id=project_definition.id,
                    path=parents,
                    is_collection=False,
                    instanciate_by_default=True,
                    order_index=index,
                    config=config,
                    default_value=value,
                )
            )

        value = self.field_config_factory.build_value(DecimalFieldConfig)
        index = len(name_map)
        name = "taxes"
        config = self.field_config_factory.build_config(name, index, config_type)
        self.db.add(
            ProjectDefinitionNodeFactory(
                name=name,
                project_definition_id=project_definition.id,
                path=parents,
                is_collection=True,
                instanciate_by_default=True,
                order_index=index,
                config=config,
                default_value=value,
            )
        )

        return self
