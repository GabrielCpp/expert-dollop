from random import choice
from dataclasses import dataclass
from faker import Faker
from expert_dollup.core.domains import *


@dataclass
class TypeFactory:
    build_value: callable
    build_config: callable


class ValueTypeFactory:
    def __init__(self, fake: Faker):
        self.fake = fake
        self.value_type_factories = {
            "INT": TypeFactory(
                build_value=self._create_int_value,
                build_config=self._create_int_custom_attr,
            ),
            "STRING": TypeFactory(
                build_value=self._create_string_value,
                build_config=self._create_string_custom_attr,
            ),
            "DECIMAL": TypeFactory(
                build_value=self._create_decimal_value,
                build_config=self._create_decimal_custom_attr,
            ),
            "BOOLEAN": TypeFactory(
                build_value=self._create_bool_value,
                build_config=self._create_bool_custom_attr,
            ),
            "CONTAINER": TypeFactory(
                build_value=self._create_container_value,
                build_config=self._create_container_custom_attr,
            ),
            "STATIC_CHOICE": TypeFactory(
                build_value=self._create_static_choice_value,
                build_config=self._create_static_choice_custom_attr,
            ),
        }

        self.field_value_types = [
            "INT",
            "STRING",
            "DECIMAL",
            "BOOLEAN",
            "STATIC_CHOICE",
        ]

    def pick_value_type(self, label):
        return "CONTAINER" if label != "field" else choice(self.field_value_types)

    def build_value(self, value_type):
        return self.value_type_factories[value_type].build_value()

    def build_config(self, label: str, index: int, value_type):
        return self.value_type_factories[value_type].build_config(label, index)

    def _create_int_value(self):
        return IntFieldValue(integer=self.fake.pyint(min_value=0, max_value=100000))

    def _create_int_custom_attr(self, label: str, index: int):
        return NodeConfig(
            value_type=IntFieldConfig(
                validator={"type": "integer", "minimum": 0, "maximum": 100000}
            )
        )

    def _create_decimal_value(self):
        return DecimalFieldValue(
            numeric=self.fake.pyfloat(right_digits=3, min_value=-10, max_value=5000)
        )

    def _create_decimal_custom_attr(self, label: str, index: int):
        return NodeConfig(
            value_type=DecimalFieldConfig(
                validator={"type": "number", "minimum": -100000, "maximum": 100000},
                precision=3,
            )
        )

    def _create_string_value(self):
        return StringFieldValue(text=" ".join(self.fake.words()))

    def _create_string_custom_attr(self, label: str, index: int):
        return NodeConfig(
            value_type=StringFieldConfig(
                validator={
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 200,
                },
                transforms=["trim"],
            )
        )

    def _create_bool_value(self):
        return BoolFieldValue(enabled=self.fake.pybool())

    def _create_bool_custom_attr(self, label: str, index: int):
        return NodeConfig(value_type=BoolFieldConfig(validator={"type": "boolean"}))

    def _create_static_choice_value(self):
        return StringFieldValue(text=str(self.fake.pyint(min_value=0, max_value=4)))

    def _create_static_choice_custom_attr(self, label: str, index: int):
        options = []

        for index in range(0, 5):
            name = "_".join(self.fake.words())
            options.append(
                StaticChoiceOption(
                    id=str(index), label=name, help_text=f"{name}_help_text"
                )
            )

        return NodeConfig(
            value_type=StaticChoiceFieldConfig(
                validator={
                    "type": "string",
                    "enum": [str(index) for index in range(0, 5)],
                },
                options=options,
            )
        )

    def _create_container_custom_attr(self, label: str, index: int):
        if label == "section":
            return NodeConfig(
                value_type=CollapsibleContainerFieldConfig(is_collapsible=index >= 3)
            )

        return NodeConfig(value_type=None)

    def _create_container_value(self):
        return None
