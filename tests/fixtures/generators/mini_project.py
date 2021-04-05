from uuid import uuid4, UUID
from faker import Faker
from typing import List
from pydantic import BaseModel
from expert_dollup.core.domains import *
from ..fake_db_helpers import FakeExpertDollupDb as Tables
from ..factories import FieldConfigFactory


class MiniProject:
    def __init__(self):
        self.tables = Tables()
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

        self.tables.project_definitions.append(project_definition)

        root = ProjectDefinitionNode(
            id=uuid4(),
            name="root",
            project_def_id=project_definition.id,
            path=[],
            is_collection=False,
            instanciate_by_default=True,
            order_index=0,
            config=NodeConfig(),
            creation_date_utc=self.fake.date_time(),
            default_value=None,
        )

        self.tables.project_definition_nodes.append(root)

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
            value = self.field_config_factory.build_value(config_type)
            config = self.field_config_factory.build_config(None, index, config_type)
            definition_container = ProjectDefinitionNode(
                id=uuid4(),
                name=name_map[config_type],
                project_def_id=project_definition.id,
                path=parents,
                is_collection=False,
                instanciate_by_default=True,
                order_index=index,
                config=config,
                creation_date_utc=self.fake.date_time(),
                default_value=value,
            )

            self.tables.project_definition_nodes.append(definition_container)

        value = self.field_config_factory.build_value(DecimalFieldConfig)
        index = len(name_map)
        label = "taxes"
        config = self.field_config_factory.build_config(label, index, config_type)
        definition_container = ProjectDefinitionNode(
            id=uuid4(),
            name=label,
            project_def_id=project_definition.id,
            path=parents,
            is_collection=True,
            instanciate_by_default=True,
            order_index=index,
            config=config,
            creation_date_utc=self.fake.date_time(),
            default_value=value,
        )

        self.tables.project_definition_nodes.append(definition_container)

        return self

    @property
    def model(self) -> Tables:
        return self.tables
