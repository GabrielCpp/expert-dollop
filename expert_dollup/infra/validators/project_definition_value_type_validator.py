from uuid import UUID
from typing import List, Dict, Awaitable, Optional
from dataclasses import dataclass, asdict
from jsonschema import Draft7Validator
from expert_dollup.core.exceptions import FactorySeedMissing
from expert_dollup.core.domains import (
    ProjectDefinitionValueType,
    NodeConfig,
    ValueUnion,
    CollapsibleContainerFieldConfig,
)
from expert_dollup.infra.json_schema import validate_instance
from expert_dollup.infra.services import ProjectDefinitionValueTypeService


@dataclass
class ValueTypeSchemas:
    attributes_json_schema: Draft7Validator
    value_json_schema: dict


class ProjectDefinitionValueTypeValidator:
    def __init__(self, value_type_service: ProjectDefinitionValueTypeService):
        self.value_type_service = value_type_service
        self.value_types: Optional[Dict[str, ValueTypeSchemas]] = None

    async def _get_values_types(self) -> Awaitable[Dict[str, ValueTypeSchemas]]:
        if self.value_types is None:
            value_types = await self.value_type_service.find_all()
            self.value_types = {
                value_type.id: ValueTypeSchemas(
                    attributes_json_schema=Draft7Validator(
                        value_type.attributes_json_schema
                    ),
                    value_json_schema=value_type.value_json_schema,
                )
                for value_type in value_types
            }

        return self.value_types

    async def validate_config(
        self, value_type_id: str, config: NodeConfig
    ) -> Awaitable:
        value_types = await self._get_values_types()

        if not value_type_id in value_types:
            raise Exception(f"Value type {value_type_id} not found.")

        value_type_schemas = value_types[value_type_id]
        validate_instance(value_type_schemas.attributes_json_schema, asdict(config))

    async def validate_value(
        self, value_type_id: str, config: NodeConfig, value: ValueUnion
    ) -> Awaitable:
        value_types = await self._get_values_types()

        if not value_type_id in value_types:
            raise FactorySeedMissing(f"Value type {value_type_id} not found.")

        value_type_schemas = value_types[value_type_id]
        """
        schema = {}
        schema.update(value_type_schemas.value_json_schema)

        if isinstance(config.value_type, CollapsibleContainerFieldConfig):
            return

        if not config.value_type is None:
            schema.update(config.value_type.validator)

        if not value is None:
            validator = Draft7Validator(schema)
            validate_instance(validator, value.value)

        TODO: Fix me
        """