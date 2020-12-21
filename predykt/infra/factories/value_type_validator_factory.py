from typing import Callable, List
from jsonschema import validate, Draft7Validator
from predykt.core.exceptions import FactorySeedMissing, ValidationError

INT_SCHEMA = {
    "type": "object",
    "properties": {
        "value": {"type": "integer"},
    },
}

DECIMAL_SCHEMA = {
    "type": "object",
    "properties": {
        "value": {"type": "number"},
    },
}

BOOLEAN_SCHEMA = {
    "type": "object",
    "properties": {
        "value": {"type": "boolean"},
    },
}

STRING_SCHEMA = {
    "type": "object",
    "properties": {
        "value": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255
        },
    },
}

CONTAINER_SCHEMA = {
    "type": "null"
}


def validate_instance(validator: Draft7Validator, instance: dict) -> None:
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    error_tuples = []

    if len(errors) > 0:
        for error in errors:
            for suberror in sorted(error.context, key=lambda e: e.schema_path):
                target = '.'.join(list(suberror.schema_path))
                message = suberror.message
                error_item = (target, message)
                error_tuples.append(error_item)

        raise ValidationError(error_tuples)


class ValueTypeValidatorFactory:
    def __init__(self):
        self._schemas = {
            'INT': Draft7Validator(INT_SCHEMA),
            'DECIMAL': Draft7Validator(DECIMAL_SCHEMA),
            'BOOL': Draft7Validator(BOOLEAN_SCHEMA),
            'STRING': Draft7Validator(STRING_SCHEMA),
            'CONTAINER': Draft7Validator(CONTAINER_SCHEMA),
        }

    def native_schemas(self) -> List[str]:
        return list(self._schemas.keys())

    def create(self, value_type: str) -> Callable[[dict], None]:
        if not value_type in self._schemas:
            raise FactorySeedMissing(f"No schema found for {value_type}")

        validator = self._schemas[value_type]

        return lambda instance: validate_instance(validator, instance)
