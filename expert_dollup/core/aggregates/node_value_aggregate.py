from expert_dollup.shared.automapping import Aggregate
from expert_dollup.infra.validators import SchemaValidator
from expert_dollup.infra.providers import ValueTypeProvider
from expert_dollup.core.exceptions import ValidationError
from expert_dollup.core.domains import (
    ValueType,
    NodeConfig,
    ValueType,
    ValueUnion,
    IntFieldConfig,
    DecimalFieldConfig,
    StaticChoiceFieldConfig,
    StringFieldConfig,
    CollapsibleContainerFieldConfig,
    BoolFieldConfig,
)
from dataclasses import asdict, dataclass


@dataclass
class ValueTypeAggregateProps:
    value_type: ValueType
    config: NodeConfig


class NodeValueAggregate(Aggregate[ValueTypeAggregateProps]):
    def __init__(
        self, schema_validator: SchemaValidator, value_type_provider: ValueTypeProvider
    ):
        self.schema_validator = schema_validator
        self.value_type_provider = value_type_provider

    def _create(self, props: ValueTypeAggregateProps) -> "NodeValueAggregate":
        schema_per_type = self.value_type_provider.get_schema_per_type()

        if not props.value_type in schema_per_type:
            raise ValidationError.for_field(
                "value_type",
                f"{props.value_type} is not an acceptable values, must be one of f{schema_per_type.keys()}",
            )

        value_type_schema = schema_per_type[props.value_type]

        if isinstance(
            props.config,
            (
                IntFieldConfig,
                DecimalFieldConfig,
                StaticChoiceFieldConfig,
                StringFieldConfig,
            ),
        ):
            self.schema_validator.is_valid_schema(value_type_schema.validator)

        self.props = props
        return self

    def validate_value(self, value: ValueUnion) -> None:
        if self.props.value_type is ValueType.BOOLEAN:
            return

        if self.props.value_type in [ValueType.CONTAINER, ValueType.SECTION_CONTAINER]:
            return

        if isinstance(
            self.props.config.value_type,
            (type(None), CollapsibleContainerFieldConfig),
        ):
            if not value is None:
                raise ValidationError.for_field("value", "Value has to be none.")
        elif isinstance(
            self.props.config,
            (
                IntFieldConfig,
                DecimalFieldConfig,
                StaticChoiceFieldConfig,
                StringFieldConfig,
            ),
        ):
            self.schema_validator.validate_instance_of(
                self.props.config.value_type.validator,
                value,
            )
