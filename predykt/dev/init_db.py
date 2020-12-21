from uuid import uuid4, UUID
from faker import Faker
from typing import List
from random import choice
from pydantic import BaseModel
from predykt.infra.predykt_db import (
    PredyktDatabase, ProjectDefinitionDao,
    ProjectDefinitionContainerDao, project_definition_table, project_definition_container_table
)


class SimpleProject:
    def __init__(self):
        self.project_container_definitions: List[ProjectDefinitionContainerDao] = [
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
                    path=[*parents],
                    mixed_paths=generate_index(parents),
                    value_type=value_type,
                    is_collection=index == 0,
                    instanciate_by_default=True,
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
            path=[],
            value_type='CONTAINER',
            is_collection=False,
            instanciate_by_default=True,
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
            path=[],
            value_type='CONTAINER',
            is_collection=True,
            instanciate_by_default=False,
            custom_attributes=dict(),
            creation_date_utc=self.fake.date_time(),
            default_value=None,
            mixed_paths=[],
        )

        self.project_container_definitions.append(root_b)
        generate_child_container(root_b, [str(root_b.id)])

    def generate(self):
        project_definition = ProjectDefinitionDao(
            id=uuid4(),
            name=''.join(self.fake.words()),
            status='OPEN',
            default_datasheet_id=uuid4(),
            creation_date_utc=self.fake.date_time(),
        )

        self.project_definitions.append(project_definition)
        self.generate_project_container_definition(project_definition.id)

    def insert(self, database):
        database.execute(
            project_definition_table.insert(),
            [element.dict() for element in self.project_definitions]
        )

        database.execute(
            project_container_definition_table.insert(),
            [element.dict() for element in self.project_container_definitions]
        )

    def json(self):
        class Tables(BaseModel):
            project_container_definitions: List[ProjectDefinitionContainerDao]
            project_definitions: List[ProjectDefinitionDao]

        return Tables(project_definitions=self.project_definitions, project_container_definitions=self.project_container_definitions).json(indent=4, sort_keys=True)


def generate_json(output_path=None):
    fixture = SimpleProject()
    fixture.generate()
    json_content = fixture.json()

    if output_path is None:
        print(json_content)
    else:
        with open(output_path, 'w') as f:
            f.write(json_content)


def generate_sql():
    import os
    from dotenv import load_dotenv
    from sqlalchemy import create_engine

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
