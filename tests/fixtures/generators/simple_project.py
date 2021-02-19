from uuid import uuid4, UUID
from faker import Faker
from typing import List
from pydantic import BaseModel
from expert_dollup.infra.path_transform import join_path
from ..fake_db_helpers import FakeExpertDollupDb as Tables
from ..factories import ValueTypeFactory
from expert_dollup.infra.path_transform import build_path_steps
from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    ProjectDefinitionDao,
    TranslationDao,
    ProjectDefinitionContainerDao,
    project_definition_table,
    project_definition_container_table,
)


class SimpleProject:
    def __init__(self):
        self.project_definition_container: List[ProjectDefinitionContainerDao] = []
        self.project_definitions: List[ProjectDefinitionDao] = []
        self.tanslations: List[TranslationDao] = []
        self.fake = Faker()
        self.value_type_factory = ValueTypeFactory(self.fake)

    def generate_project_container_definition(self, project_def_id: UUID) -> None:
        labels = ["root", "subsection", "form", "section", "field"]

        def generate_child_container(
            direct_parent: ProjectDefinitionContainerDao, parents: List[str]
        ) -> None:
            level = len(parents)

            if level >= len(labels):
                return

            label = labels[level]

            for index in range(0, level + 1):
                value_type = self.value_type_factory.pick_value_type(label)
                value = self.value_type_factory.build_value(value_type)
                config = self.value_type_factory.build_config(label, index, value_type)
                other_field = {}

                if not value is None:
                    other_field["default_value"] = value

                sub_container = ProjectDefinitionContainerDao(
                    id=uuid4(),
                    name=f"{direct_parent.name}_{label}_{index}",
                    project_def_id=project_def_id,
                    path=join_path(parents),
                    mixed_paths=build_path_steps(parents),
                    value_type=value_type,
                    is_collection=index == 0,
                    instanciate_by_default=True,
                    order_index=index,
                    config=config,
                    creation_date_utc=self.fake.date_time(),
                    **other_field,
                )

                self.project_definition_container.append(sub_container)
                generate_child_container(
                    sub_container, [*parents, str(sub_container.id)]
                )

        root_a = ProjectDefinitionContainerDao(
            id=uuid4(),
            name="root_a",
            project_def_id=project_def_id,
            path="",
            value_type="CONTAINER",
            is_collection=False,
            instanciate_by_default=True,
            order_index=0,
            config=dict(),
            creation_date_utc=self.fake.date_time(),
            default_value=self.value_type_factory.build_value("CONTAINER"),
            mixed_paths=[],
        )

        self.project_definition_container.append(root_a)
        generate_child_container(root_a, [str(root_a.id)])

        root_b = ProjectDefinitionContainerDao(
            id=uuid4(),
            name="root_b",
            project_def_id=project_def_id,
            path="",
            value_type="CONTAINER",
            is_collection=True,
            instanciate_by_default=False,
            order_index=1,
            config=dict(),
            creation_date_utc=self.fake.date_time(),
            default_value=self.value_type_factory.build_value("CONTAINER"),
            mixed_paths=[],
        )

        self.project_definition_container.append(root_b)
        generate_child_container(root_b, [str(root_b.id)])

    def generate_project_definition(self):
        project_definition = ProjectDefinitionDao(
            id=uuid4(),
            name="".join(self.fake.words()),
            status="OPEN",
            default_datasheet_id=uuid4(),
            creation_date_utc=self.fake.date_time(),
        )

        self.project_definitions.append(project_definition)
        self.generate_project_container_definition(project_definition.id)

    def generate_translations(self):
        for project_container_definition in self.project_definition_container:
            self.tanslations.append(
                TranslationDao(
                    ressource_id=self.project_definitions[0].id,
                    scope=project_container_definition.id,
                    locale="fr",
                    name=project_container_definition.name,
                    value=" ".join(self.fake.words()),
                )
            )

            self.tanslations.append(
                TranslationDao(
                    ressource_id=self.project_definitions[0].id,
                    scope=project_container_definition.id,
                    locale="fr",
                    name=f"{project_container_definition.name}_helptext",
                    value=self.fake.sentence(nb_words=20),
                )
            )

            self.tanslations.append(
                TranslationDao(
                    ressource_id=self.project_definitions[0].id,
                    scope=project_container_definition.id,
                    locale="en",
                    name=project_container_definition.name,
                    value=" ".join(self.fake.words()),
                )
            )

            self.tanslations.append(
                TranslationDao(
                    ressource_id=self.project_definitions[0].id,
                    scope=project_container_definition.id,
                    locale="en",
                    name=f"{project_container_definition.name}_helptext",
                    value=self.fake.sentence(nb_words=20),
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
            project_definition_containers=self.project_definition_container,
            translations=self.tanslations,
        )
