from uuid import UUID
from typing import List
from expert_dollup.core.domains import *
from ..fake_db_helpers import FakeDb, DbFixtureGenerator
from ..factories import FieldConfigFactory
from ..factories_domain import *


class SimpleProject(DbFixtureGenerator):
    def __init__(self):
        self._db = FakeDb()
        self.field_config_factory = FieldConfigFactory()

    @property
    def db(self) -> FakeDb:
        return self._db

    def generate_project_node_definition(self, project_def_id: UUID) -> None:
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
                value = self.field_config_factory.build_value(config_type)
                name = f"{direct_parent.name}_{label}_{index}"
                config = self.field_config_factory.build_config(
                    name, index, config_type
                )

                sub_node = ProjectDefinitionNodeFactory(
                    name=name,
                    project_def_id=project_def_id,
                    path=parents,
                    is_collection=index == 0,
                    instanciate_by_default=True,
                    order_index=index,
                    config=config,
                    default_value=value,
                )

                self.db.add(sub_node)
                generate_child_node(sub_node, [*parents, str(sub_node.id)])

        root_a = ProjectDefinitionNodeFactory(
            name="root_a",
            project_def_id=project_def_id,
            path=[],
            is_collection=False,
            instanciate_by_default=True,
            order_index=0,
            config=NodeConfig(
                translations=TranslationConfig(
                    help_text_name="root_a_text", label="root_a"
                ),
            ),
            default_value=None,
        )

        self.db.add(root_a)
        generate_child_node(root_a, [str(root_a.id)])

        root_b = ProjectDefinitionNodeFactory(
            name="root_b",
            project_def_id=project_def_id,
            path=[],
            is_collection=True,
            instanciate_by_default=False,
            order_index=1,
            config=NodeConfig(
                translations=TranslationConfig(
                    help_text_name="root_b_text", label="root_b"
                ),
            ),
            default_value=None,
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
                    locale="fr_CA",
                    name=project_node_definition.config.translations.label,
                )
            )

            self.db.add(
                TranslationFactory(
                    ressource_id=project_definition.id,
                    scope=project_node_definition.id,
                    locale="fr_CA",
                    name=project_node_definition.config.translations.help_text_name,
                )
            )

            self.db.add(
                TranslationFactory(
                    ressource_id=project_definition.id,
                    scope=project_node_definition.id,
                    locale="en_US",
                    name=project_node_definition.config.translations.label,
                )
            )

            self.db.add(
                TranslationFactory(
                    ressource_id=project_definition.id,
                    scope=project_node_definition.id,
                    locale="en_US",
                    name=project_node_definition.config.translations.help_text_name,
                )
            )

            if isinstance(
                project_node_definition.config.field_details, StaticChoiceFieldConfig
            ):
                for option in project_node_definition.config.field_details.options:
                    self.db.add(
                        TranslationFactory(
                            ressource_id=project_definition.id,
                            scope=project_node_definition.id,
                            locale="en_US",
                            name=option.label,
                        )
                    )

                    self.db.add(
                        TranslationFactory(
                            ressource_id=project_definition.id,
                            scope=project_node_definition.id,
                            locale="en_US",
                            name=option.help_text,
                        )
                    )

    def generate(self):
        self.generate_project_definition()
        self.generate_translations()
        return self
