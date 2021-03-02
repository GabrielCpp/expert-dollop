from uuid import UUID, uuid4
from typing import Awaitable
from datetime import datetime
from dataclasses import asdict
from expert_dollup.core.exceptions import ValidationError
from expert_dollup.core.domains import (
    Datasheet,
    DatasheetElement,
    DatasheetFilter,
    DatasheetElementFilter,
)
from expert_dollup.infra.services import (
    DatasheetService,
    DatasheetDefinitionElementService,
    DatasheetElementService,
)
from expert_dollup.infra.validators.schema_validator import SchemaValidator


class DatasheetUseCase:
    def __init__(
        self,
        datasheet_service: DatasheetService,
        datsheet_element_service: DatasheetElementService,
        schema_validator: SchemaValidator,
        datsheet_definition_element_service: DatasheetDefinitionElementService,
    ):
        self.datasheet_service = datasheet_service
        self.datsheet_element_service = datsheet_element_service
        self.datsheet_definition_element_service = datsheet_definition_element_service
        self.schema_validator = schema_validator

    async def find_by_id(self, datasheet_id: UUID) -> Awaitable[Datasheet]:
        return await self.datasheet_service.find_by_id(datasheet_id)

    async def add(self, datasheet: Datasheet) -> Awaitable[Datasheet]:
        await self.datasheet_service.add(datasheet)
        definition_elements = await self.datsheet_definition_element_service.find_all()
        elements = [
            DatasheetElement(
                datasheet_id=datasheet.id,
                element_def_id=definition_element.id,
                child_element_reference=uuid4(),
                properties=[
                    default_property.value
                    for default_property in definition_element.default_properties
                ],
                original_datasheet_id=datasheet.id,
                creation_date_utc=datetime.utcnow(),
            )
            for definition_element in definition_elements
        ]

        await self.datsheet_definition_element_service.insert_many(elements)
        return await self.datasheet_service.find_by_id(datasheet_id)

    async def update(self, datasheet: Datasheet) -> Awaitable[Datasheet]:
        await self.datasheet_service.update(
            DatasheetFilter(**asdict(datasheet)), DatasheetFilter(id=datasheet.id)
        )
        return await self.datasheet_service.find_by_id(datasheet_id)

    async def delete(self, datasheet_id: UUID) -> Awaitable:
        await self.datsheet_element_service.remove_by(
            DatasheetElementFilter(datasheet_id=datasheet_id)
        )
        await self.datasheet_service.delete_by_id(datasheet.id)
