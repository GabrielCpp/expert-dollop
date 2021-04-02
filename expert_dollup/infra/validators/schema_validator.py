from jsonschema import Draft7Validator
from expert_dollup.infra.json_schema import validate_instance


class SchemaValidator:
    def __init__(self):
        pass

    def is_valid_schema(self, schema) -> bool:
        try:
            Draft7Validator(schema)
        except:
            return False

        return True

    def validate_instance_of(self, schema: dict, instance: dict) -> None:
        validator = Draft7Validator(schema)
        validate_instance(validator, instance)
