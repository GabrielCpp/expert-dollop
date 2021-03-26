from uuid import uuid4, UUID
from faker import Faker
from typing import List
from pydantic import BaseModel
from expert_dollup.core.domains import *
from ..fake_db_helpers import FakeExpertDollupDb as Tables
from ..factories import ValueTypeFactory


class MiniProject:
    def __init__(self):
        self.tables = Tables()
        self.fake = Faker()
        self.fake.seed_instance(seed=1)
        self.value_type_factory = ValueTypeFactory(self.fake)

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
            value_type="CONTAINER",
            is_collection=False,
            instanciate_by_default=True,
            order_index=0,
            config=NodeConfig(),
            creation_date_utc=self.fake.date_time(),
            default_value=self.value_type_factory.build_value("CONTAINER"),
        )

        self.tables.project_definition_nodes.append(root)

        name_map = {
            "INT": "quantity",
            "STRING": "item_name",
            "DECIMAL": "price",
            "BOOLEAN": "is_confirmed",
            "STATIC_CHOICE": "item_size",
        }

        parents = [root.id]
        for index, value_type in enumerate(self.value_type_factory.field_value_types):
            value = self.value_type_factory.build_value(value_type)
            config = self.value_type_factory.build_config(None, index, value_type)
            definition_container = ProjectDefinitionNode(
                id=uuid4(),
                name=name_map[value_type],
                project_def_id=project_definition.id,
                path=parents,
                value_type=value_type,
                is_collection=False,
                instanciate_by_default=True,
                order_index=index,
                config=config,
                creation_date_utc=self.fake.date_time(),
                default_value=value,
            )

            self.tables.project_definition_nodes.append(definition_container)

        value_type = "DECIMAL"
        value = self.value_type_factory.build_value(value_type)
        index = len(name_map)
        label = "taxes"
        config = self.value_type_factory.build_config(label, index, value_type)
        definition_container = ProjectDefinitionNode(
            id=uuid4(),
            name=label,
            project_def_id=project_definition.id,
            path=parents,
            value_type=value_type,
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
