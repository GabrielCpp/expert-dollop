from jsonschema import Draft7Validator
from expert_dollup.core.exceptions import ValidationError

BOOL_JSON_SCHEMA = {"type": "boolean"}
INT_JSON_SCHEMA = {"type": "integer", "minimum": 0, "maximum": 100000}
NUMBER_JSON_SCHEMA = {"type": "number", "minimum": -100000, "maximum": 100000}
STRING_JSON_SCHEMA = {
    "type": "string",
    "minLength": 1,
    "maxLength": 200,
}


def validate_instance(validator: Draft7Validator, instance: dict) -> None:
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    error_tuples = []

    if len(errors) > 0:
        for error in errors:
            for suberror in sorted(error.context, key=lambda e: e.schema_path):
                target = ".".join(list(suberror.schema_path))
                message = suberror.message
                error_item = (target, message)
                error_tuples.append(error_item)
            else:
                target = ".".join(list(error.schema_path))
                message = error.message
                error_item = (target, message)
                error_tuples.append(error_item)

        raise ValidationError(error_tuples)
