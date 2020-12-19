import os
from predykt.infra.predykt_db import (
    PredyktDatabase, ProjectDefinitionDao,
    ProjectContainerDefinitionDao, project_definition_table, project_container_definition_table
)

from uuid import uuid4, UUID
from faker import Faker
from typing import List
from random import choice
from dotenv import load_dotenv
from sqlalchemy import create_engine
import json


class SimpleProject:
    def __init__(self):
        self.project_container_definitions: List[ProjectContainerDefinitionDao] = [
        ]
        self.project_definitions: List[ProjectDefinitionDao] = []
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
            combinaisons = [*parents]

            for index in range(2, len(parents)):
                combinaisons.append('/'.join(combinaisons[0:index]))

            return combinaisons

        def generate_child_container(direct_parent: ProjectContainerDefinitionDao, parents: List[str]) -> None:
            level = len(parents)

            if level > len(labels):
                return

            for index in range(0, level + 1):
                value_type = 'CONTAINER' if level < 5 else choice(value_types)
                value_gen = value_type_map[value_type] if value_type in value_type_map else None
                sub_container = ProjectContainerDefinitionDao(
                    id=uuid4(),
                    name=direct_parent.name + '_' +
                    labels[level - 1] + '_' + str(index),
                    project_def_id=project_def_id,
                    path_type=generate_index(parents),
                    value_type=value_type,
                    is_collection=index == 0,
                    attributes=dict(),
                    creation_date=self.fake.date_time(),
                    default_value=None if value_gen is None else dict(
                        value=value_gen())
                )

                self.project_container_definitions.append(sub_container)
                generate_child_container(
                    sub_container, [*parents, str(sub_container.id)])

        root_a = ProjectContainerDefinitionDao(
            id=uuid4(),
            name='root_a',
            project_def_id=project_def_id,
            path_type=[],
            value_type='CONTAINER',
            is_collection=False,
            attributes=dict(),
            creation_date=self.fake.date_time(),
            default_value=None
        )

        self.project_container_definitions.append(root_a)
        generate_child_container(root_a, [str(root_a.id)])

        root_b = ProjectContainerDefinitionDao(
            id=uuid4(),
            name='root_b',
            project_def_id=project_def_id,
            path_type=[],
            value_type='CONTAINER',
            is_collection=True,
            attributes=dict(),
            creation_date=self.fake.date_time(),
            default_value=None
        )

        self.project_container_definitions.append(root_b)
        generate_child_container(root_b, [str(root_b.id)])

    def generate(self):
        project_definition = ProjectDefinitionDao(
            id=uuid4(),
            name=''.join(self.fake.words()),
            status='OPEN',
            default_datasheet_id=uuid4(),
            owner_id=uuid4(),
            creation_date=self.fake.date_time(),
        )

        self.project_definitions.append(project_definition)
        generate_project_container_definition(project_definition.id)

    def insert(self, database):
        database.execute(
            project_definition_table.insert(),
            [element.dict() for element in self.project_definition]
        )

        database.execute(
            project_container_definition_table.insert(),
            [element.dict() for element in self.project_container_definitions]
        )

    def dict():
        return {
            'project_container_definitions': [element.dict() for element in self.project_container_definitions],
            'project_definition_table': [element.dict() for element in self.project_definition],
        }


if __name__ == "__main__":
    load_dotenv()
    DATABASE_URL = "postgres://{}:{}@{}/{}".format(
        os.environ["POSTGRES_USERNAME"],
        os.environ["POSTGRES_PASSWORD"],
        os.environ["POSTGRES_HOST"],
        os.environ["POSTGRES_DB"]
    )

    engine = create_engine(DATABASE_URL)

    with engine.connect() as connection:
        fixture = SimpleProject()
        fixture.generate()
        fixture.insert(connection)
