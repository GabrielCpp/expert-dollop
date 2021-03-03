from uuid import UUID
from typing import Awaitable
from expert_dollup.core.exceptions import ValidationError
from expert_dollup.core.domains import DatasheetElement
from expert_dollup.infra.services import (
    DatasheetElementService,
    DatasheetDefinitionElementService,
)
from expert_dollup.infra.validators.schema_validator import SchemaValidator


class DatasheetElementUseCase:
    def __init__(
        self,
        datasheet_element_service: DatasheetElementService,
        datasheet_definition_element_service: DatasheetDefinitionElementService,
        schema_validator: SchemaValidator,
    ):
        self.datasheet_element_service = datasheet_element_service
        self.schema_validator = schema_validator

    async def find_all_by_page(self, datsheet_id: UUID):
        return await self.datasheet_element_service.find_all_by_page(datsheet_id)

    async def update(self, datsheet_id, child_reference_id, properties):
        (
            target_datsheet_id,
            element_def_id,
        ) = await self.datasheet_element_service.get_full_id(child_reference_id)

        if target_datsheet_id != datsheet_id:
            raise Exception()

        element_def = self.datasheet_definition_element_service.find_by_id(
            element_def_id
        )
        await self.datasheet_element_service.update()

    async def add_to_collection(self, element: DatasheetElement):
        pass

    async def delete_collection_item(self):
        pass
