from uuid import uuid4, UUID
from faker import Faker
from typing import List
from random import choice
from pydantic import BaseModel
from dataclasses import dataclass
from expert_dollup.infra.path_transform import join_path
from .tables import Tables
from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    ProjectDefinitionDao,
    TranslationDao,
    ProjectDefinitionContainerDao,
    project_definition_table,
    project_definition_container_table,
)


@dataclass
class TypeFactory:
    build_value: callable
    build_custom_attr: callable


class ValueTypeFactory:
    def __init__(self, fake: Faker):
        self.fake = fake
        self.value_type_factories = {
            "INT": TypeFactory(
                build_value=self._create_int_value,
                build_custom_attr=self._create_int_custom_attr,
            ),
            "STRING": TypeFactory(
                build_value=self._create_string_value,
                build_custom_attr=self._create_string_custom_attr,
            ),
            "DECIMAL": TypeFactory(
                build_value=self._create_decimal_value,
                build_custom_attr=self._create_decimal_custom_attr,
            ),
            "BOOL": TypeFactory(
                build_value=self._create_bool_value,
                build_custom_attr=self._create_bool_custom_attr,
            ),
            "CONTAINER": TypeFactory(
                build_value=lambda: None,
                build_custom_attr=self._create_container_custom_attr,
            ),
            "STATIC_CHOICE": TypeFactory(
                build_value=self._create_static_choice_value,
                build_custom_attr=self._create_static_choice_custom_attr,
            ),
        }

        self.field_value_types = ["INT", "STRING", "DECIMAL", "BOOL", "STATIC_CHOICE"]

    def pick_value_type(self, label):
        return "CONTAINER" if label != "field" else choice(self.field_value_types)

    def build_value(self, value_type):
        return self.value_type_factories[value_type].build_value()

    def build_custom_attr(self, label: str, index: int, value_type):
        return self.value_type_factories[value_type].build_custom_attr(label, index)

    def _create_int_value(self):
        return {"value": self.fake.pyint(min_value=0, max_value=100000)}

    def _create_int_custom_attr(self, label: str, index: int):
        return {
            "value_type": {
                "validator": {"type": "integer", "minimum": 0, "maximum": 100000}
            }
        }

    def _create_decimal_value(self):
        return {
            "value": self.fake.pyfloat(right_digits=3, min_value=-10, max_value=5000)
        }

    def _create_decimal_custom_attr(self, label: str, index: int):
        return {
            "value_type": {
                "validator": {"type": "number", "minimum": -100000, "maximum": 100000},
                "precision": 3,
            }
        }

    def _create_string_value(self):
        return {"value": " ".join(self.fake.words())}

    def _create_string_custom_attr(self, label: str, index: int):
        return {
            "value_type": {
                "validator": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 200,
                },
                "transforms": ["trim"],
            }
        }

    def _create_bool_value(self):
        return {"value": self.fake.pybool()}

    def _create_bool_custom_attr(self, label: str, index: int):
        return {"value_type": {"validator": {"type": "boolean"}}}

    def _create_static_choice_value(self):
        return {"value": str(self.fake.pyint(min_value=0, max_value=4))}

    def _create_static_choice_custom_attr(self, label: str, index: int):
        options = []

        for index in range(0, 5):
            name = "_".join(self.fake.words())
            options.append(
                {"id": str(index), "label": name, "help_text": f"{name}_help_text"}
            )

        return {
            "value_type": {
                "validator": {
                    "type": "string",
                    "enum": [str(index) for index in range(0, 5)],
                },
                "options": options,
            },
        }

    def _create_container_custom_attr(self, label: str, index: int):
        if label == "section":
            return {
                "value_type": {
                    "is_collapsible": index >= 3,
                },
            }

        return {}


class SimpleProject:
    def __init__(self):
        self.project_container_definitions: List[ProjectDefinitionContainerDao] = []
        self.project_definitions: List[ProjectDefinitionDao] = []
        self.tanslations: List[TranslationDao] = []
        self.fake = Faker()
        self.value_type_factory = ValueTypeFactory(self.fake)

    def generate_project_container_definition(self, project_def_id: UUID) -> None:
        labels = ["root", "subsection", "form", "section", "field"]

        def generate_index(parents: List[str]):
            combinaisons = []

            for index in range(2, len(parents)):
                combinaisons.append("/".join(combinaisons[0:index]))

            return combinaisons

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
                custom_attributes = self.value_type_factory.build_custom_attr(
                    label, index, value_type
                )
                other_field = {}

                if not value is None:
                    other_field["default_value"] = value

                sub_container = ProjectDefinitionContainerDao(
                    id=uuid4(),
                    name=f"{direct_parent.name}_{label}_{index}",
                    project_def_id=project_def_id,
                    path=join_path(parents),
                    mixed_paths=generate_index(parents),
                    value_type=value_type,
                    is_collection=index == 0,
                    instanciate_by_default=True,
                    order_index=index,
                    custom_attributes=custom_attributes,
                    creation_date_utc=self.fake.date_time(),
                    **other_field,
                )

                self.project_container_definitions.append(sub_container)
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
            custom_attributes=dict(),
            creation_date_utc=self.fake.date_time(),
            default_value=None,
            mixed_paths=[],
        )

        self.project_container_definitions.append(root_a)
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
            name="".join(self.fake.words()),
            status="OPEN",
            default_datasheet_id=uuid4(),
            creation_date_utc=self.fake.date_time(),
        )

        self.project_definitions.append(project_definition)
        self.generate_project_container_definition(project_definition.id)

    def generate_translations(self):
        for project_container_definition in self.project_container_definitions:
            self.tanslations.append(
                TranslationDao(
                    ressource_id=self.project_definitions[0].id,
                    locale="fr",
                    name=project_container_definition.name,
                    value=" ".join(self.fake.words()),
                )
            )

            self.tanslations.append(
                TranslationDao(
                    ressource_id=self.project_definitions[0].id,
                    locale="fr",
                    name=f"{project_container_definition.name}_helptext",
                    value=self.fake.sentence(nb_words=20),
                )
            )

            self.tanslations.append(
                TranslationDao(
                    ressource_id=self.project_definitions[0].id,
                    locale="en",
                    name=project_container_definition.name,
                    value=" ".join(self.fake.words()),
                )
            )

            self.tanslations.append(
                TranslationDao(
                    ressource_id=self.project_definitions[0].id,
                    locale="en",
                    name=f"{project_container_definition.name}_helptext",
                    value=self.fake.sentence(nb_words=20),
                )
            )

    def generate(self):
        self.generate_project_definition()
        self.generate_translations()

    def model(self) -> Tables:
        return Tables(
            project_definitions=self.project_definitions,
            project_container_definitions=self.project_container_definitions,
            translations=self.tanslations,
        )
