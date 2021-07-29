from datetime import datetime, timezone, timedelta
from uuid import uuid4, UUID
from faker import Faker
from typing import List
from pydantic import BaseModel
from expert_dollup.core.domains import *
from ..fake_db_helpers import FakeExpertDollupDb as Tables
from ..factories import FieldConfigFactory


class ProjectWithTrigger:
    def __init__(self):
        self.model = Tables()
        self.fake = Faker()
        self.fake.seed_instance(seed=1)
        self.field_config_factory = FieldConfigFactory(self.fake)
        self.labels = ["root", "subsection", "form", "section", "field"]

    def generate(self):
        project_definition = ProjectDefinition(
            id=uuid4(),
            name="".join(self.fake.words()),
            default_datasheet_id=uuid4(),
            datasheet_def_id=uuid4(),
            creation_date_utc=self.fake.date_time(),
        )

        self.model.project_definitions.append(project_definition)

        root_a = ProjectDefinitionNode(
            id=uuid4(),
            name="root_a",
            project_def_id=project_definition.id,
            path=[],
            is_collection=False,
            instanciate_by_default=True,
            order_index=0,
            config=NodeConfig(
                translation=TranslationConfig(
                    help_text_name="root_a_text", label="root_a"
                ),
            ),
            creation_date_utc=self.fake.date_time(tzinfo=timezone.utc),
            default_value=None,
        )
        subsection_a = self._create_container_node(root_a)
        form_a = self._create_container_node(subsection_a)
        section_a = self._create_section_node(form_a)

        self.model.project_definition_nodes.append(root_a)
        self.model.project_definition_nodes.append(subsection_a)
        self.model.project_definition_nodes.append(form_a)
        self.model.project_definition_nodes.append(section_a)

        root_b = ProjectDefinitionNode(
            id=uuid4(),
            name="root_b",
            project_def_id=project_definition.id,
            path=[],
            is_collection=True,
            instanciate_by_default=False,
            order_index=1,
            config=NodeConfig(
                translation=TranslationConfig(
                    help_text_name="root_b_text", label="root_b"
                ),
            ),
            creation_date_utc=self.fake.date_time(tzinfo=timezone.utc),
            default_value=None,
        )

        field_a = self._create_checkbox_field(section_a, root_b.id)
        self.model.project_definition_nodes.append(field_a)

        subsection_b = self._create_container_node(root_b)
        form_b = self._create_container_node(subsection_b)
        section_b = self._create_section_node(form_b)
        field_b = self._create_textfield(section_b, root_b.id)

        self.model.project_definition_nodes.append(root_b)
        self.model.project_definition_nodes.append(subsection_b)
        self.model.project_definition_nodes.append(form_b)
        self.model.project_definition_nodes.append(section_b)
        self.model.project_definition_nodes.append(field_b)

        return self

    def _create_container_node(
        self, parent: ProjectDefinitionNode, is_collection: bool = False
    ):
        level = len(parent.path)
        label = self.labels[level]
        name = f"{parent.name}_{label}_0"
        config = self.field_config_factory.build_config(name, 0)

        node = ProjectDefinitionNode(
            id=uuid4(),
            name=name,
            project_def_id=parent.project_def_id,
            path=parent.subpath,
            is_collection=is_collection,
            instanciate_by_default=True,
            order_index=0,
            config=config,
            creation_date_utc=self.fake.date_time(tzinfo=timezone.utc),
            default_value=None,
        )

        return node

    def _create_section_node(
        self, parent: ProjectDefinitionNode, is_collection: bool = False
    ):
        level = len(parent.path)
        label = self.labels[level]
        name = f"{parent.name}_{label}_0"
        config = self.field_config_factory.build_config(
            name, 0, CollapsibleContainerFieldConfig
        )
        value = self.field_config_factory.build_value(CollapsibleContainerFieldConfig)

        node = ProjectDefinitionNode(
            id=uuid4(),
            name=name,
            project_def_id=parent.project_def_id,
            path=parent.subpath,
            is_collection=is_collection,
            instanciate_by_default=True,
            order_index=0,
            config=config,
            creation_date_utc=self.fake.date_time(tzinfo=timezone.utc),
            default_value=value,
        )

        return node

    def _create_checkbox_field(
        self, parent: ProjectDefinitionNode, target_type_id: UUID
    ):
        level = len(parent.path)
        label = self.labels[level]
        name = f"{parent.name}_{label}_0"
        config = self.field_config_factory.build_config(name, 0, BoolFieldConfig)
        value = self.field_config_factory.build_value(BoolFieldConfig)
        value = False

        config.triggers.append(
            Trigger(
                action=TriggerAction.SET_VISIBILITY,
                target_type_id=target_type_id,
                params={},
            )
        )

        node = ProjectDefinitionNode(
            id=uuid4(),
            name=name,
            project_def_id=parent.project_def_id,
            path=parent.subpath,
            is_collection=False,
            instanciate_by_default=True,
            order_index=0,
            config=config,
            creation_date_utc=self.fake.date_time(tzinfo=timezone.utc),
            default_value=value,
        )

        return node

    def _create_textfield(self, parent: ProjectDefinitionNode, target_type_id: UUID):
        level = len(parent.path)
        label = self.labels[level]
        name = f"{parent.name}_{label}_0"
        config = self.field_config_factory.build_config(name, 0, StringFieldConfig)
        value = self.field_config_factory.build_value(StringFieldConfig)

        config.triggers.append(
            Trigger(
                action=TriggerAction.CHANGE_NAME,
                target_type_id=target_type_id,
                params={},
            )
        )

        node = ProjectDefinitionNode(
            id=uuid4(),
            name=name,
            project_def_id=parent.project_def_id,
            path=parent.subpath,
            is_collection=False,
            instanciate_by_default=True,
            order_index=0,
            config=config,
            creation_date_utc=self.fake.date_time(tzinfo=timezone.utc),
            default_value=value,
        )

        return node