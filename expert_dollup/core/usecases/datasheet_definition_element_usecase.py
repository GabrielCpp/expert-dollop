from uuid import UUID
from typing import Awaitable
from expert_dollup.core.exceptions import ValidationError
from expert_dollup.core.domains import DatasheetDefinitionElement
from expert_dollup.infra.services import (
    DatasheetDefinitionService,
    DatasheetDefinitionElementService,
)
from expert_dollup.infra.validators.schema_validator import SchemaValidator


class DatasheetDefinitionElementUseCase:
    def __init__(
        self,
        datasheet_definition_service: DatasheetDefinitionService,
        datasheet_definition_element_service: DatasheetDefinitionElementService,
        schema_validator: SchemaValidator,
    ):
        self.datasheet_definition_service = datasheet_definition_service
        self.datasheet_definition_element_service = datasheet_definition_element_service
        self.schema_validator = schema_validator

    async def find_by_id(self, id: UUID):
        return await self.datasheet_definition_element_service.find_by_id(id)

    async def add(
        self, datasheet_definition_element: DatasheetDefinitionElement
    ) -> Awaitable[DatasheetDefinitionElement]:
        await self._validate_element(datasheet_definition_element)
        await self.datasheet_definition_element_service.insert(
            datasheet_definition_element
        )
        return datasheet_definition_element

    async def update(
        self, datasheet_definition_element: DatasheetDefinitionElement
    ) -> Awaitable[DatasheetDefinitionElement]:
        await self._validate_element(datasheet_definition_element)
        await self.datasheet_definition_element_service.update(
            datasheet_definition_element
        )
        return await self.datasheet_definition_element_service.find_by_id(
            datasheet_definition_element.id
        )

    async def delete_by_id(self, id: UUID) -> Awaitable:
        await self.datasheet_definition_element_service.delete_by_id(id)

    async def _validate_element(
        self,
        datasheet_definition_element: DatasheetDefinitionElement,
    ) -> Awaitable:
        datasheet_definition = await self.datasheet_definition_service.find_by_id(
            datasheet_definition_element.datasheet_def_id
        )

        properties_schema = datasheet_definition.properties

        for name, schema in properties_schema.items():
            property_instance = datasheet_definition_element.default_properties.get(
                name
            )

            if property_instance is None:
                raise ValidationError.for_field(
                    f"default_properties.{name}", "Field not set"
                )

            self.schema_validator.validate_instance_of(
                schema.value_validator, property_instance.value
            )
