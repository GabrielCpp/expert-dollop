from uuid import UUID
from expert_dollup.core.domains import *
from ..fake_db_helpers import FakeDb
from ..factories import FieldConfigFactory
from ..factories_domain import *


class ProjectWithTrigger:
    def __init__(self):
        self.db = FakeDb()
        self.field_config_factory = FieldConfigFactory()
        self.labels = ["root", "subsection", "form", "section", "field"]

    def __call__(self):
        project_definition = ProjectDefinitionFactory()
        self.db.add(project_definition)

        root_a = ProjectDefinitionNodeFactory(
            name="root_a",
            project_definition_id=project_definition.id,
            path=[],
            is_collection=False,
            instanciate_by_default=True,
            order_index=0,
            config=NodeConfig(
                translations=TranslationConfig(
                    help_text_name="root_a_text", label="root_a"
                ),
                meta=NodeMetaConfig(is_visible=True),
            ),
            default_value=None,
        )
        subsection_a = self._create_container_node(root_a)
        form_a = self._create_container_node(subsection_a)
        section_a = self._create_section_node(form_a)

        self.db.add(root_a)
        self.db.add(subsection_a)
        self.db.add(form_a)
        self.db.add(section_a)

        root_b = ProjectDefinitionNodeFactory(
            name="root_b",
            project_definition_id=project_definition.id,
            path=[],
            is_collection=True,
            instanciate_by_default=False,
            order_index=1,
            config=NodeConfig(
                translations=TranslationConfig(
                    help_text_name="root_b_text", label="root_b"
                ),
                meta=NodeMetaConfig(is_visible=False),
            ),
            default_value=None,
        )

        field_a = self._create_checkbox_field(section_a, root_b.id)
        self.db.add(field_a)

        subsection_b = self._create_container_node(root_b)
        form_b = self._create_container_node(subsection_b)
        section_b = self._create_section_node(form_b)
        field_b = self._create_textfield(section_b, root_b.id)

        self.db.add(root_b)
        self.db.add(subsection_b)
        self.db.add(form_b)
        self.db.add(section_b)
        self.db.add(field_b)

        return self.db

    def _create_container_node(
        self, parent: ProjectDefinitionNode, is_collection: bool = False
    ):
        level = len(parent.path)
        label = self.labels[level]
        name = f"{parent.name}_{label}_0"
        config = self.field_config_factory.build_config(name, 0)

        node = ProjectDefinitionNodeFactory(
            name=name,
            project_definition_id=parent.project_definition_id,
            path=parent.subpath,
            is_collection=is_collection,
            instanciate_by_default=True,
            order_index=0,
            config=config,
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

        node = ProjectDefinitionNodeFactory(
            name=name,
            project_definition_id=parent.project_definition_id,
            path=parent.subpath,
            is_collection=is_collection,
            instanciate_by_default=True,
            order_index=0,
            config=config,
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

        node = ProjectDefinitionNodeFactory(
            name=name,
            project_definition_id=parent.project_definition_id,
            path=parent.subpath,
            is_collection=False,
            instanciate_by_default=True,
            order_index=0,
            config=config,
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

        node = ProjectDefinitionNodeFactory(
            name=name,
            project_definition_id=parent.project_definition_id,
            path=parent.subpath,
            is_collection=False,
            instanciate_by_default=True,
            order_index=0,
            config=config,
            default_value=value,
        )

        return node
