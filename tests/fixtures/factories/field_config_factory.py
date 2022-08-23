from random import choice
from dataclasses import dataclass
from faker import Faker
from decimal import Decimal
from expert_dollup.core.domains import *


class FieldConfigFactory:
    def __init__(self):
        self.fake = Faker()
        self.node_factory = {
            IntFieldConfig: self._create_int_custom_attr,
            StringFieldConfig: self._create_string_custom_attr,
            DecimalFieldConfig: self._create_decimal_custom_attr,
            BoolFieldConfig: self._create_bool_custom_attr,
            CollapsibleContainerFieldConfig: self._create_node_custom_attr,
            StaticChoiceFieldConfig: self._create_static_choice_custom_attr,
            None: self._empty_field_details,
        }

        self.field_config_types = [
            IntFieldConfig,
            DecimalFieldConfig,
            StringFieldConfig,
            BoolFieldConfig,
            StaticChoiceFieldConfig,
        ]

    def pick_config_type(self, level_label: str) -> FieldDetailsUnion:
        if level_label == "section":
            return CollapsibleContainerFieldConfig

        if level_label == "field":
            return choice(self.field_config_types)

        return None

    def build(self, name: str, index: int, config_type=None):
        return self.node_factory[config_type](name, index)

    def _create_int_custom_attr(self, name: str, index: int):
        return IntFieldConfig(
            unit="inch", default_value=self.fake.pyint(min_value=0, max_value=100000)
        )

    def _create_decimal_custom_attr(self, name: str, index: int):
        return DecimalFieldConfig(
            unit="pound",
            precision=3,
            default_value=self.fake.pydecimal(
                right_digits=3, min_value=-10, max_value=5000
            ),
        )

    def _create_string_custom_attr(self, name: str, index: int):
        return StringFieldConfig(
            transforms=["trim"], default_value=" ".join(self.fake.words())
        )

    def _create_bool_custom_attr(self, name: str, index: int):
        return BoolFieldConfig(default_value=self.fake.pybool())

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

        return StaticChoiceFieldConfig(
            options=options,
            default_value=str(self.fake.pyint(min_value=0, max_value=4)),
        )

    def _create_node_custom_attr(self, name: str, index: int):
        return CollapsibleContainerFieldConfig(is_collapsible=index >= 3)

    def _empty_field_details(self, name: str, index: int):
        return None
