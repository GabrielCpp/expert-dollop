from uuid import UUID
from typing import List
from expert_dollup.core.domains import *
from ..fake_db_helpers import FakeDb
from ..factories_domain import *
from .field_config_factory import FieldConfigFactory


class SimpleProject:
    def __init__(self):
        self.field_config_factory = FieldConfigFactory()

    def generate_project_node_definition(self, project_definition_id: UUID) -> None:
        labels = ["root", "subsection", "form", "section", "field"]

        def generate_child_node(
            direct_parent: ProjectDefinitionNode, parents: List[str]
        ) -> None:
            level = len(parents)

            if level >= len(labels):
                return

            label = labels[level]

            for index in range(0, level + 1):
                config_type = self.field_config_factory.pick_config_type(label)
                name = f"{direct_parent.name}_{label}_{index}"
                field_details = self.field_config_factory.build(
                    name, index, config_type
                )
                sub_node = ProjectDefinitionNodeFactory(
                    name=name,
                    project_definition_id=project_definition_id,
                    path=parents,
                    is_collection=index == 0,
                    instanciate_by_default=True,
                    ordinal=index,
                    field_details=field_details,
                )

                self.db.add(sub_node)
                generate_child_node(sub_node, [*parents, str(sub_node.id)])

        root_a = ProjectDefinitionNodeFactory(
            name="root_a",
            project_definition_id=project_definition_id,
            path=[],
            is_collection=False,
            instanciate_by_default=True,
            ordinal=0,
            translations=TranslationConfig(
                help_text_name="root_a_text", label="root_a"
            ),
        )

        self.db.add(root_a)
        generate_child_node(root_a, [str(root_a.id)])

        root_b = ProjectDefinitionNodeFactory(
            name="root_b",
            project_definition_id=project_definition_id,
            path=[],
            is_collection=True,
            instanciate_by_default=False,
            ordinal=1,
            translations=TranslationConfig(
                help_text_name="root_b_text", label="root_b"
            ),
        )

        self.db.add(root_b)
        generate_child_node(root_b, [str(root_b.id)])

    def generate_project_definition(self):
        project_definition = ProjectDefinitionFactory()
        self.db.add(project_definition)
        self.generate_project_node_definition(project_definition.id)

    def generate_translations(self):
        project_definition = self.db.get_only_one(ProjectDefinition)

        for project_node_definition in self.db.all(ProjectDefinitionNode):
            self.db.add(
                TranslationFactory(
                    ressource_id=project_definition.id,
                    scope=project_node_definition.id,
                    locale="fr-CA",
                    name=project_node_definition.translations.label,
                )
            )

            self.db.add(
                TranslationFactory(
                    ressource_id=project_definition.id,
                    scope=project_node_definition.id,
                    locale="fr-CA",
                    name=project_node_definition.translations.help_text_name,
                )
            )

            self.db.add(
                TranslationFactory(
                    ressource_id=project_definition.id,
                    scope=project_node_definition.id,
                    locale="en-US",
                    name=project_node_definition.translations.label,
                )
            )

            self.db.add(
                TranslationFactory(
                    ressource_id=project_definition.id,
                    scope=project_node_definition.id,
                    locale="en-US",
                    name=project_node_definition.translations.help_text_name,
                )
            )

            if isinstance(
                project_node_definition.field_details, StaticChoiceFieldConfig
            ):
                for option in project_node_definition.field_details.options:
                    self.db.add(
                        TranslationFactory(
                            ressource_id=project_definition.id,
                            scope=project_node_definition.id,
                            locale="en-US",
                            name=option.label,
                        )
                    )

                    self.db.add(
                        TranslationFactory(
                            ressource_id=project_definition.id,
                            scope=project_node_definition.id,
                            locale="en-US",
                            name=option.help_text,
                        )
                    )

    def __call__(self, db: FakeDb) -> None:
        self.db = db
        self.generate_project_definition()
        self.generate_translations()
