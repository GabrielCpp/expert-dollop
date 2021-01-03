from uuid import uuid4, UUID
from faker import Faker
from typing import List
from random import choice
from pydantic import BaseModel
from predykt.infra.path_transform import join_path
from .tables import Tables
from predykt.infra.predykt_db import (
    PredyktDatabase, ProjectDefinitionDao, ProjectDefinitionPluginDao, TranslationDao,
    ProjectDefinitionContainerDao, project_definition_table, project_definition_container_table
)


class SimpleProject:
    def __init__(self):
        self.project_container_definitions: List[ProjectDefinitionContainerDao] = [
        ]
        self.project_definitions: List[ProjectDefinitionDao] = []
        self.project_definition_plugins: List[ProjectDefinitionPluginDao] = []
        self.tanslations: List[TranslationDao] = []
        self.fake = Faker()

    def generate_project_container_definition(self, project_def_id: UUID) -> None:
        labels = [
            'subsection',
            'form',
            'section',
            'field'
        ]

        value_type_map = {
            'INT': self.fake.pyint,
            'STRING': self.fake.words,
            'DECIMAL': lambda: self.fake.pyfloat(right_digits=2),
            'BOOL': self.fake.pybool,
        }

        value_types = list(value_type_map.keys())

        def generate_index(parents: List[str]):
            combinaisons = []

            for index in range(2, len(parents)):
                combinaisons.append('/'.join(combinaisons[0:index]))

            return combinaisons

        def generate_child_container(direct_parent: ProjectDefinitionContainerDao, parents: List[str]) -> None:
            level = len(parents)

            if level > len(labels):
                return

            for index in range(0, level + 1):
                value_type = 'CONTAINER' if level < 5 else choice(value_types)
                value_gen = value_type_map[value_type] if value_type in value_type_map else None
                sub_container = ProjectDefinitionContainerDao(
                    id=uuid4(),
                    name=direct_parent.name + '_' +
                    labels[level - 1] + '_' + str(index),
                    project_def_id=project_def_id,
                    path=join_path(parents),
                    mixed_paths=generate_index(parents),
                    value_type=value_type,
                    is_collection=index == 0,
                    instanciate_by_default=True,
                    order_index=index,
                    custom_attributes=dict(),
                    creation_date_utc=self.fake.date_time(),
                    default_value=None if value_gen is None else dict(
                        value=value_gen())
                )

                self.project_container_definitions.append(sub_container)
                generate_child_container(
                    sub_container, [*parents, str(sub_container.id)])

        root_a = ProjectDefinitionContainerDao(
            id=uuid4(),
            name='root_a',
            project_def_id=project_def_id,
            path='',
            value_type='CONTAINER',
            is_collection=False,
            instanciate_by_default=True,
            order_index=0,
            custom_attributes=dict(),
            creation_date_utc=self.fake.date_time(),
            default_value=None,
            mixed_paths=[],
        )

        self.project_container_definitions.append(root_a)
        generate_child_container(root_a, [str(root_a.id)])

        root_b = ProjectDefinitionContainerDao(
            id=uuid4(),
            name='root_b',
            project_def_id=project_def_id,
            path='',
            value_type='CONTAINER',
            is_collection=True,
            instanciate_by_default=False,
            order_index=1,
            custom_attributes=dict(),
            creation_date_utc=self.fake.date_time(),
            default_value=None,
            mixed_paths=[],
        )

        self.project_container_definitions.append(root_b)
        generate_child_container(root_b, [str(root_b.id)])

    def generate_project_definition(self):
        project_definition = ProjectDefinitionDao(
            id=uuid4(),
            name=''.join(self.fake.words()),
            status='OPEN',
            default_datasheet_id=uuid4(),
            creation_date_utc=self.fake.date_time(),
            plugins=[UUID("986663da-e409-430b-a8d1-489666ef1719")]
        )

        self.project_definitions.append(project_definition)
        self.generate_project_container_definition(project_definition.id)

    def generate_plugins(self):
        pass
        """
        translation_plugin = ProjectDefinitionPluginDao(
            id=UUID("986663da-e409-430b-a8d1-489666ef1719"),
            name="translation",
            validation_schema={
                "type": "object",
                "properties": {
                    "tooltip"
                }
            },
            default_config={}
            form_config=''
            node_condition={
                condition: [
                    "$in", [
                        "container_type",
                        ":container_type"
                    ] 
                ],
                parameters: {
                    "container_type": ["CONTAINER", "INTEGER", ""]
                }
            }
        )
        """

    def generate_translations(self):
        for project_container_definition in self.project_container_definitions:
            self.tanslations.append(TranslationDao(
                ressource_id=self.project_definitions[0].id,
                locale='fr',
                name=project_container_definition.name,
                value=' '.join(self.fake.words())
            ))

            self.tanslations.append(TranslationDao(
                ressource_id=self.project_definitions[0].id,
                locale='fr',
                name=f"{project_container_definition.name}_helptext",
                value=self.fake.sentence(nb_words=20)
            ))

            self.tanslations.append(TranslationDao(
                ressource_id=self.project_definitions[0].id,
                locale='en',
                name=project_container_definition.name,
                value=' '.join(self.fake.words())
            ))

            self.tanslations.append(TranslationDao(
                ressource_id=self.project_definitions[0].id,
                locale='en',
                name=f"{project_container_definition.name}_helptext",
                value=self.fake.sentence(nb_words=20)
            ))

    def generate(self):
        self.generate_plugins()
        self.generate_project_definition()
        self.generate_translations()

    def model(self) -> Tables:
        return Tables(
            project_definitions=self.project_definitions,
            project_container_definitions=self.project_container_definitions,
            translations=self.tanslations
        )
