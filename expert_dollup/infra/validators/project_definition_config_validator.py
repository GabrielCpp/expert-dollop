from uuid import UUID
from typing import List, Dict
from jsonschema import Draft7Validator
from expert_dollup.infra.json_schema import validate_instance


class ProjectDefinitionConfigValidator:
    def build_schema(self, plugins_schema: Dict[str, dict]) -> dict:
        return {"type": "object", "properties": plugins_schema}

    def validate(
        self, custom_attributes: dict, plugins_schema: Dict[str, dict]
    ) -> None:
        full_schema = self.build_schema(plugins_schema)
        validator = Draft7Validator(full_schema)
        validate_instance(validator, custom_attributes)
