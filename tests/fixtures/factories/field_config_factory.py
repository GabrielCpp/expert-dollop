from random import choice
from dataclasses import dataclass
from faker import Faker
from sqlalchemy.sql.expression import label
from expert_dollup.core.domains import *


@dataclass
class TypeFactory:
    build_value: callable
    build_config: callable


class FieldConfigFactory:
    def __init__(self, fake: Faker):
        self.fake = fake
        self.node_factory = {
            IntFieldConfig: TypeFactory(
                build_value=self._create_int_value,
                build_config=self._create_int_custom_attr,
            ),
            StringFieldConfig: TypeFactory(
                build_value=self._create_string_value,
                build_config=self._create_string_custom_attr,
            ),
            DecimalFieldConfig: TypeFactory(
                build_value=self._create_decimal_value,
                build_config=self._create_decimal_custom_attr,
            ),
            BoolFieldConfig: TypeFactory(
                build_value=self._create_bool_value,
                build_config=self._create_bool_custom_attr,
            ),
            CollapsibleContainerFieldConfig: TypeFactory(
                build_value=self._create_node_value,
                build_config=self._create_node_custom_attr,
            ),
            StaticChoiceFieldConfig: TypeFactory(
                build_value=self._create_static_choice_value,
                build_config=self._create_static_choice_custom_attr,
            ),
            None: TypeFactory(
                build_value=self._create_node_value,
                build_config=self._create_build_config,
            ),
        }

        self.field_config_types = [
            IntFieldConfig,
            DecimalFieldConfig,
            StringFieldConfig,
            BoolFieldConfig,
            StaticChoiceFieldConfig,
        ]

    def pick_config_type(self, label) -> FieldDetailsUnion:
        if label == "section":
            return CollapsibleContainerFieldConfig

        if label == "field":
            return choice(self.field_config_types)

        return None

    def build_value(self, config_type):
        return self.node_factory[config_type].build_value()

    def build_config(self, label: str, index: int, config_type):
        return self.node_factory[config_type].build_config(label, index)

    def _create_int_value(self):
        return self.fake.pyint(min_value=0, max_value=100000)

    def _create_int_custom_attr(self, name: str, index: int):
        return NodeConfig(
            field_details=IntFieldConfig(unit="inch"),
            value_validator={"type": "integer", "minimum": 0, "maximum": 100000},
            translation=TranslationConfig(
                help_text_name=f"{name}_help_text", label=name
            ),
        )

    def _create_decimal_value(self):
        return self.fake.pyfloat(right_digits=3, min_value=-10, max_value=5000)

    def _create_decimal_custom_attr(self, name: str, index: int):
        return NodeConfig(
            field_details=DecimalFieldConfig(
                unit="pound",
                precision=3,
            ),
            value_validator={"type": "number", "minimum": -100000, "maximum": 100000},
            translation=TranslationConfig(
                help_text_name=f"{name}_help_text", label=name
            ),
        )

    def _create_string_value(self):
        return " ".join(self.fake.words())

    def _create_string_custom_attr(self, name: str, index: int):
        return NodeConfig(
            field_details=StringFieldConfig(
                transforms=["trim"],
            ),
            value_validator={
                "type": "string",
                "minLength": 1,
                "maxLength": 200,
            },
            translation=TranslationConfig(
                help_text_name=f"{name}_help_text", label=name
            ),
        )

    def _create_bool_value(self):
        return self.fake.pybool()

    def _create_bool_custom_attr(self, name: str, index: int):
        return NodeConfig(
            field_details=BoolFieldConfig(is_checkbox=True),
            value_validator={"type": "boolean"},
            translation=TranslationConfig(
                help_text_name=f"{name}_help_text", label=name
            ),
        )

    def _create_static_choice_value(self):
        return str(self.fake.pyint(min_value=0, max_value=4))

    def _create_static_choice_custom_attr(self, name: str, index: int):
        options = []

        for index in range(0, 5):
            option_name = "_".join(self.fake.words())
            options.append(
                StaticChoiceOption(
                    id=str(index),
                    label=option_name,
                    help_text=f"{option_name}_help_text",
                )
            )

        return NodeConfig(
            field_details=StaticChoiceFieldConfig(
                options=options,
            ),
            value_validator={
                "type": "string",
                "enum": [str(index) for index in range(0, 5)],
            },
            translation=TranslationConfig(
                help_text_name=f"{name}_help_text", label=name
            ),
        )

    def _create_node_custom_attr(self, name: str, index: int):
        return NodeConfig(
            field_details=CollapsibleContainerFieldConfig(is_collapsible=index >= 3),
            value_validator=None,
            translation=TranslationConfig(
                help_text_name=f"{name}_help_text", label=name
            ),
        )

    def _create_node_value(self):
        return None

    def _create_build_config(self, name: str, index: int):
        return NodeConfig(
            translation=TranslationConfig(
                help_text_name=f"{name}_help_text", label=name
            )
        )
