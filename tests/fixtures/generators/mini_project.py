from uuid import uuid4
from faker import Faker
from expert_dollup.core.domains import *
from ..fake_db_helpers import FakeDb
from ..factories import FieldConfigFactory


class MiniProject:
    def __init__(self):
        self.db = FakeDb()
        self.fake = Faker()
        self.fake.seed_instance(seed=1)
        self.field_config_factory = FieldConfigFactory(self.fake)

    def generate(self):
        project_definition = ProjectDefinition(
            id=uuid4(),
            name="".join(self.fake.words()),
            default_datasheet_id=uuid4(),
            datasheet_def_id=uuid4(),
            creation_date_utc=self.fake.date_time(),
        )

        self.db.add(project_definition)

        root = ProjectDefinitionNode(
            id=uuid4(),
            name="root",
            project_def_id=project_definition.id,
            path=[],
            is_collection=False,
            instanciate_by_default=True,
            order_index=0,
            config=NodeConfig(
                translations=TranslationConfig(
                    help_text_name="root_help_text", label="root"
                ),
            ),
            creation_date_utc=self.fake.date_time(),
            default_value=None,
        )

        self.db.add(root)

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
            definition_node = ProjectDefinitionNode(
                id=uuid4(),
                name=name,
                project_def_id=project_definition.id,
                path=parents,
                is_collection=False,
                instanciate_by_default=True,
                order_index=index,
                config=config,
                creation_date_utc=self.fake.date_time(),
                default_value=value,
            )

            self.db.add(definition_node)

        value = self.field_config_factory.build_value(DecimalFieldConfig)
        index = len(name_map)
        name = "taxes"
        config = self.field_config_factory.build_config(name, index, config_type)
        definition_node = ProjectDefinitionNode(
            id=uuid4(),
            name=name,
            project_def_id=project_definition.id,
            path=parents,
            is_collection=True,
            instanciate_by_default=True,
            order_index=index,
            config=config,
            creation_date_utc=self.fake.date_time(),
            default_value=value,
        )

        self.db.add(definition_node)

        return self
