from expert_dollup.shared.automapping import Aggregate
from expert_dollup.infra.validators import SchemaValidator
from expert_dollup.core.exceptions import ValidationError
from expert_dollup.core.domains import *
from dataclasses import asdict, dataclass


@dataclass
class NodeValue:
    config: NodeConfig
    value: ValueUnion


class NodeValueAggregate(Aggregate[NodeValue]):
    def __init__(self, schema_validator: SchemaValidator):
        self.schema_validator = schema_validator

    def _create(self, props: NodeValue) -> "NodeValueAggregate":
        if props.config.value_validator is None:
            if not props.value is None:
                raise ValidationError.for_field(
                    "value", "Value must be null as value validator is null"
                )
        else:
            self.schema_validator.is_valid_schema(props.config.value_validator)
            self.schema_validator.validate_instance_of(
                props.config.value_validator, props.value
            )

        self.props = props
        return self
