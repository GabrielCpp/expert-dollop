from uuid import UUID
from expert_dollup.core.domains import *
from ..fake_db_helpers import FakeDb
from ..factories import FieldConfigFactory
from ..factories_domain import *


class ProjectWithTrigger:
    def __init__(self):
        self.field_config_factory = FieldConfigFactory()
        self.labels = ["root", "subsection", "form", "section", "field"]

    def __call__(self, db: FakeDb) -> None:
        project_definition = ProjectDefinitionFactory()
        db.add(project_definition)

        root_a = ProjectDefinitionNodeFactory(
            name="root_a",
            project_definition_id=project_definition.id,
            path=[],
            is_collection=False,
            instanciate_by_default=True,
            order_index=0,
            translations=TranslationConfig(
                help_text_name="root_a_text", label="root_a"
            ),
            meta=NodeMetaConfig(is_visible=True),
        )
        subsection_a = self._create_container_node(root_a)
        form_a = self._create_container_node(subsection_a)
        section_a = self._create_section_node(form_a)

        db.add(root_a)
        db.add(subsection_a)
        db.add(form_a)
        db.add(section_a)

        root_b = ProjectDefinitionNodeFactory(
            name="root_b",
            project_definition_id=project_definition.id,
            path=[],
            is_collection=True,
            instanciate_by_default=False,
            order_index=1,
            translations=TranslationConfig(
                help_text_name="root_b_text", label="root_b"
            ),
            meta=NodeMetaConfig(is_visible=False),
        )

        field_a = self._create_checkbox_field(section_a, root_b.id)
        db.add(field_a)

        subsection_b = self._create_container_node(root_b)
        form_b = self._create_container_node(subsection_b)
        section_b = self._create_section_node(form_b)
        field_b = self._create_textfield(section_b, root_b.id)

        db.add(root_b)
        db.add(subsection_b)
        db.add(form_b)
        db.add(section_b)
        db.add(field_b)

    def _create_container_node(
        self, parent: ProjectDefinitionNode, is_collection: bool = False
    ):
        level = len(parent.path)
        label = self.labels[level]
        name = f"{parent.name}_{label}_0"
        field_details = self.field_config_factory.build(name, 0)
        node = ProjectDefinitionNodeFactory(
            name=name,
            project_definition_id=parent.project_definition_id,
            path=parent.subpath,
            is_collection=is_collection,
            instanciate_by_default=True,
            order_index=0,
            field_details=field_details,
        )

        return node

    def _create_section_node(
        self, parent: ProjectDefinitionNode, is_collection: bool = False
    ):
        level = len(parent.path)
        label = self.labels[level]
        name = f"{parent.name}_{label}_0"
        field_details = self.field_config_factory.build(
            name, 0, CollapsibleContainerFieldConfig
        )
        node = ProjectDefinitionNodeFactory(
            name=name,
            project_definition_id=parent.project_definition_id,
            path=parent.subpath,
            is_collection=is_collection,
            instanciate_by_default=True,
            order_index=0,
            field_details=field_details,
        )

        return node

    def _create_checkbox_field(
        self, parent: ProjectDefinitionNode, target_type_id: UUID
    ):
        level = len(parent.path)
        label = self.labels[level]
        name = f"{parent.name}_{label}_0"
        node = ProjectDefinitionNodeFactory(
            name=name,
            project_definition_id=parent.project_definition_id,
            path=parent.subpath,
            is_collection=False,
            instanciate_by_default=True,
            order_index=0,
            field_details=BoolFieldConfig(default_value=False),
            triggers=[
                Trigger(
                    action=TriggerAction.SET_VISIBILITY,
                    target_type_id=target_type_id,
                    params={},
                )
            ],
        )

        return node

    def _create_textfield(self, parent: ProjectDefinitionNode, target_type_id: UUID):
        level = len(parent.path)
        label = self.labels[level]
        name = f"{parent.name}_{label}_0"
        field_details = self.field_config_factory.build(name, 0, StringFieldConfig)
        node = ProjectDefinitionNodeFactory(
            name=name,
            project_definition_id=parent.project_definition_id,
            path=parent.subpath,
            is_collection=False,
            instanciate_by_default=True,
            order_index=0,
            field_details=field_details,
            triggers=[
                Trigger(
                    action=TriggerAction.CHANGE_NAME,
                    target_type_id=target_type_id,
                    params={},
                )
            ],
        )

        return node
