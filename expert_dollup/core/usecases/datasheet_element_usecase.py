from uuid import UUID, uuid4
from typing import Awaitable, Dict, Union, Optional
from dataclasses import asdict
from expert_dollup.shared.database_services import Page
from expert_dollup.core.exceptions import ValidationError, InvalidUsageError
from expert_dollup.core.domains import (
    Datasheet,
    DatasheetElement,
    DatasheetFilter,
    DatasheetElementFilter,
    DatasheetElementId,
    DatasheetDefinitionElement,
    DatasheetDefinition,
    DatasheetCloneTarget,
)
from expert_dollup.infra.services import (
    DatasheetService,
    DatasheetDefinitionElementService,
    DatasheetElementService,
    DatasheetDefinitionService,
)
from expert_dollup.infra.validators.schema_validator import SchemaValidator
from expert_dollup.shared.starlette_injection import Clock


class DatasheetElementUseCase:
    def __init__(
        self,
        datasheet_service: DatasheetService,
        datasheet_element_service: DatasheetElementService,
        schema_validator: SchemaValidator,
        datasheet_definition_element_service: DatasheetDefinitionElementService,
        datsheet_definition_service: DatasheetDefinitionService,
        clock: Clock,
    ):
        self.datasheet_service = datasheet_service
        self.datasheet_element_service = datasheet_element_service
        self.datasheet_definition_element_service = datasheet_definition_element_service
        self.schema_validator = schema_validator
        self.datsheet_definition_service = datsheet_definition_service
        self.clock = clock

    async def find_datasheet_elements(
        self, datasheet_id: UUID, limit: int, next_page_token: Optional[str] = None
    ) -> Awaitable[Page[DatasheetElement]]:
        return await self.datasheet_element_service.find_by_paginated(
            DatasheetElementFilter(datasheet_id=datasheet_id),
            limit,
            next_page_token,
        )

    async def find_datasheet_element(
        self, id: DatasheetElementId
    ) -> Awaitable[DatasheetElement]:
        return await self.datasheet_element_service.find_by_id(id)

    async def update_datasheet_element_properties(
        self, id: DatasheetElementId, properties: Dict[str, Union[float, str, bool]]
    ) -> Awaitable[DatasheetElement]:
        datsheet: Datasheet = await self.datasheet_service.find_by_id(id.datasheet_id)
        datsheet_definition: DatasheetDefinition = (
            await self.datsheet_definition_service.find_by_id(datsheet.datasheet_def_id)
        )
        element_definition: DatasheetDefinitionElement = (
            await self.datasheet_definition_element_service.find_by_id(
                id.element_def_id
            )
        )

        self._validate_datsheet_element_properties(
            properties, datsheet_definition, element_definition
        )

        await self.datasheet_element_service.update(
            DatasheetElementFilter(properties=properties),
            DatasheetElementFilter(
                datasheet_id=id.datasheet_id,
                element_def_id=id.element_def_id,
                child_element_reference=id.child_element_reference,
            ),
        )

        return await self.datasheet_element_service.find_by_id(id)

    async def add_collection_item(
        self, datasheet_id: UUID, element_def_id: UUID, properties: UUID
    ) -> Awaitable[DatasheetElement]:
        datsheet: Datasheet = await self.datasheet_service.find_by_id(datasheet_id)
        datsheet_definition: DatasheetDefinition = (
            await self.datsheet_definition_service.find_by_id(datsheet.datasheet_def_id)
        )
        element_definition: DatasheetDefinitionElement = (
            await self.datasheet_definition_element_service.find_by_id(element_def_id)
        )

        if not element_definition.is_collection:
            raise InvalidUsageError("Non collection element cannot be instanciated.")

        self._validate_datsheet_element_properties(
            properties, datsheet_definition, element_definition
        )

        new_element = DatasheetElement(
            datasheet_id=datasheet_id,
            element_def_id=element_def_id,
            child_element_reference=uuid4(),
            properties=properties,
            original_datasheet_id=datasheet_id,
            creation_date_utc=self.clock.utcnow(),
        )
        await self.datasheet_element_service.insert(new_element)

        return new_element

    async def delete_element(self, element_id: DatasheetElementId) -> Awaitable:
        element_definition: DatasheetDefinitionElement = (
            await self.datasheet_definition_element_service.find_by_id(
                element_id.element_def_id
            )
        )

        if not element_definition.is_collection:
            raise InvalidUsageError("Non collection element cannot be instanciated.")

        collection_size = await self.datasheet_element_service.get_collection_size(
            element_id.datasheet_id, element_id.element_def_id
        )

        if collection_size <= 1:
            raise InvalidUsageError("Cannot delete all items of collection")

        await self.datasheet_element_service.delete_by_id(element_id)

    def _validate_datsheet_element_properties(
        self,
        properties: Dict[str, Union[float, str, bool]],
        datsheet_definition: DatasheetDefinition,
        element_definition: DatasheetDefinitionElement,
    ):
        for name, default_property in element_definition.default_properties.items():
            if name in properties:
                if default_property.is_readonly is True:
                    raise ValidationError.for_field(name, "Field is readonly")

                assert name in datsheet_definition.element_properties_schema
                property_schema = datsheet_definition.element_properties_schema[name]
                self.schema_validator.validate_instance_of(
                    property_schema, properties[name]
                )

            elif default_property.is_readonly is False:
                raise ValidationError.for_field(name, "Field is missing")

        for name in properties.keys():
            if not name in datsheet_definition.element_properties_schema:
                raise ValidationError.for_field(name, "Field does not exist")