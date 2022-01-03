from expert_dollup.infra.validators import SchemaValidator
from expert_dollup.core.exceptions import ValidationError
from expert_dollup.core.domains import *


class NodeValueValidation:
    def __init__(self, schema_validator: SchemaValidator):
        self.schema_validator = schema_validator

    def validate_value(self, config: NodeConfig, value: PrimitiveWithNoneUnion) -> None:
        if config.value_validator is None:
            if not value is None:
                raise ValidationError.for_field(
                    "value", "Value must be null as value validator is null"
                )
        else:
            self.schema_validator.is_valid_schema(config.value_validator)
            self.schema_validator.validate_instance_of(config.value_validator, value)
