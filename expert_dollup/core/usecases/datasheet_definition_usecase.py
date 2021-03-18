from uuid import UUID
from typing import Awaitable
from expert_dollup.core.exceptions import ValidationError
from expert_dollup.core.domains import DatasheetDefinition
from expert_dollup.infra.services import DatasheetDefinitionService
from expert_dollup.infra.validators.schema_validator import SchemaValidator


class DatasheetDefinitionUseCase:
    def __init__(
        self,
        datasheet_definition_service: DatasheetDefinitionService,
        schema_validator: SchemaValidator,
    ):
        self.datasheet_definition_service = datasheet_definition_service
        self.schema_validator = schema_validator

    async def find_by_id(self, id: UUID):
        return await self.datasheet_definition_service.find_by_id(id)

    async def add(
        self, datasheet_definition: DatasheetDefinition
    ) -> Awaitable[DatasheetDefinition]:
        self.validate_datsheet(datasheet_definition)
        await self.datasheet_definition_service.insert(datasheet_definition)
        return await self.datasheet_definition_service.find_by_id(
            datasheet_definition.id
        )

    async def update(
        self, datasheet_definition: DatasheetDefinition
    ) -> Awaitable[DatasheetDefinition]:
        self.validate_datsheet(datasheet_definition)
        await self.datasheet_definition_service.update(datasheet_definition)
        return await self.datasheet_definition_service.find_by_id(
            datasheet_definition.id
        )

    async def delete_by_id(self, id: UUID) -> Awaitable:
        await self.datasheet_definition_service.delete_by_id(id)

    def validate_datsheet(self, datasheet_definition: DatasheetDefinition):
        for name, schema in datasheet_definition.element_properties_schema.items():
            if not self.schema_validator.is_valid_schema(schema):
                raise ValidationError.for_field(
                    f"element_properties_schema.{name}", "Invalid schema"
                )
