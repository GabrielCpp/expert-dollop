from uuid import uuid4, UUID
from datetime import timezone
from faker import Faker
from typing import List
from pydantic import BaseModel
from expert_dollup.core.domains import *
from ..fake_db_helpers import FakeExpertDollupDb as Tables
from ..factories import FieldConfigFactory


class SimpleProject:
    def __init__(self):
        self.project_definition_nodes: List[ProjectDefinitionNode] = []
        self.project_definitions: List[ProjectDefinition] = []
        self.tanslations: List[Translation] = []
        self.fake = Faker()
        self.field_config_factory = FieldConfigFactory(self.fake)

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
                other_field = {}

                sub_node = ProjectDefinitionNode(
                    id=uuid4(),
                    name=name,
                    project_def_id=project_def_id,
                    path=parents,
                    is_collection=index == 0,
                    instanciate_by_default=True,
                    order_index=index,
                    config=config,
                    creation_date_utc=self.fake.date_time(tzinfo=timezone.utc),
                    default_value=value,
                )

                self.project_definition_nodes.append(sub_node)
                generate_child_node(sub_node, [*parents, str(sub_node.id)])

        root_a = ProjectDefinitionNode(
            id=uuid4(),
            name="root_a",
            project_def_id=project_def_id,
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

        self.project_definition_nodes.append(root_a)
        generate_child_node(root_a, [str(root_a.id)])

        root_b = ProjectDefinitionNode(
            id=uuid4(),
            name="root_b",
            project_def_id=project_def_id,
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

        self.project_definition_nodes.append(root_b)
        generate_child_node(root_b, [str(root_b.id)])

    def generate_project_definition(self):
        project_definition = ProjectDefinition(
            id=uuid4(),
            name="".join(self.fake.words()),
            default_datasheet_id=uuid4(),
            datasheet_def_id=uuid4(),
            creation_date_utc=self.fake.date_time(tzinfo=timezone.utc),
        )

        self.project_definitions.append(project_definition)
        self.generate_project_node_definition(project_definition.id)

    def generate_translations(self):
        for project_node_definition in self.project_definition_nodes:
            self.tanslations.append(
                Translation(
                    id=uuid4(),
                    ressource_id=self.project_definitions[0].id,
                    scope=project_node_definition.id,
                    locale="fr",
                    name=project_node_definition.name,
                    value=" ".join(self.fake.words()),
                    creation_date_utc=self.fake.date_time(tzinfo=timezone.utc),
                )
            )

            self.tanslations.append(
                Translation(
                    id=uuid4(),
                    ressource_id=self.project_definitions[0].id,
                    scope=project_node_definition.id,
                    locale="fr",
                    name=f"{project_node_definition.name}_helptext",
                    value=self.fake.sentence(nb_words=20),
                    creation_date_utc=self.fake.date_time(tzinfo=timezone.utc),
                )
            )

            self.tanslations.append(
                Translation(
                    id=uuid4(),
                    ressource_id=self.project_definitions[0].id,
                    scope=project_node_definition.id,
                    locale="en",
                    name=project_node_definition.name,
                    value=" ".join(self.fake.words()),
                    creation_date_utc=self.fake.date_time(tzinfo=timezone.utc),
                )
            )

            self.tanslations.append(
                Translation(
                    id=uuid4(),
                    ressource_id=self.project_definitions[0].id,
                    scope=project_node_definition.id,
                    locale="en",
                    name=f"{project_node_definition.name}_helptext",
                    value=self.fake.sentence(nb_words=20),
                    creation_date_utc=self.fake.date_time(tzinfo=timezone.utc),
                )
            )

    def generate(self):
        self.generate_project_definition()
        self.generate_translations()
        return self

    @property
    def model(self) -> Tables:
        return Tables(
            project_definitions=self.project_definitions,
            project_definition_nodes=self.project_definition_nodes,
            translations=self.tanslations,
        )
