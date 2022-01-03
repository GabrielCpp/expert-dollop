from uuid import UUID, uuid4
from typing import List
from expert_dollup.core.domains.datasheet_definition_element import (
    DatasheetDefinitionElementFilter,
)
from expert_dollup.shared.database_services import Page
from expert_dollup.core.domains import (
    Datasheet,
    DatasheetElement,
    DatasheetFilter,
    DatasheetElementFilter,
    DatasheetCloneTarget,
    zero_uuid,
)
from expert_dollup.infra.services import (
    DatasheetService,
    DatasheetDefinitionElementService,
    DatasheetElementService,
)
from expert_dollup.infra.validators.schema_validator import SchemaValidator
from expert_dollup.shared.starlette_injection import Clock


class DatasheetUseCase:
    def __init__(
        self,
        datasheet_service: DatasheetService,
        datasheet_element_service: DatasheetElementService,
        schema_validator: SchemaValidator,
        datasheet_definition_element_service: DatasheetDefinitionElementService,
        clock: Clock,
    ):
        self.datasheet_service = datasheet_service
        self.datasheet_element_service = datasheet_element_service
        self.datasheet_definition_element_service = datasheet_definition_element_service
        self.schema_validator = schema_validator
        self.clock = clock

    async def find_by_id(self, datasheet_id: UUID) -> Datasheet:
        return await self.datasheet_service.find_by_id(datasheet_id)

    async def clone(self, datasheet_clone_target: DatasheetCloneTarget):
        datasheet = await self.datasheet_service.find_by_id(
            datasheet_clone_target.target_datasheet_id
        )
        cloned_datasheet = Datasheet(
            id=uuid4(),
            name=datasheet.name,
            is_staged=datasheet.is_staged,
            datasheet_def_id=datasheet.datasheet_def_id,
            from_datasheet_id=datasheet_clone_target.target_datasheet_id,
            creation_date_utc=self.clock.utcnow(),
        )

        page = Page[DatasheetElement]()
        cloned_elements = []

        while len(page.results) == page.limit:
            page = await self.datasheet_element_service.find_by_paginated(
                DatasheetElementFilter(
                    datasheet_id=datasheet_clone_target.target_datasheet_id
                ),
                page.limit,
                page.next_page_token,
            )
            cloned_elements.extend(
                [
                    DatasheetElement(
                        datasheet_id=cloned_datasheet.id,
                        element_def_id=result.definition_element.id,
                        child_element_reference=zero_uuid()
                        if result.child_element_reference == zero_uuid()
                        else uuid4(),
                        properties=result.properties,
                        original_datasheet_id=result.original_datasheet_id,
                        creation_date_utc=self.clock.utcnow(),
                    )
                    for result in page.results
                ]
            )

        cloned_datasheet = Datasheet(
            id=uuid4(),
            name=datasheet_clone_target.new_name,
            is_staged=datasheet.is_staged,
            datasheet_def_id=datasheet.datasheet_def_id,
            from_datasheet_id=datasheet.from_datasheet_id,
            creation_date_utc=self.clock.utcnow(),
        )

        await self.add(cloned_datasheet)
        await self.datasheet_definition_element_service.insert_many(cloned_elements)

        return cloned_datasheet

    async def add(self, datasheet: Datasheet) -> Datasheet:
        await self.datasheet_service.insert(datasheet)

    async def add_filled_datasheet(self, datasheet: Datasheet) -> Datasheet:
        await self.datasheet_service.insert(datasheet)
        definition_elements = await self.datasheet_definition_element_service.find_by(
            DatasheetDefinitionElementFilter(
                datasheet_def_id=datasheet.datasheet_def_id
            )
        )

        elements = [
            DatasheetElement(
                datasheet_id=datasheet.id,
                element_def_id=definition_element.id,
                child_element_reference=zero_uuid(),
                properties={
                    name: default_property.value
                    for name, default_property in definition_element.default_properties.items()
                },
                original_datasheet_id=datasheet.id,
                creation_date_utc=self.clock.utcnow(),
            )
            for definition_element in definition_elements
        ]

        await self.datasheet_element_service.insert_many(elements)
        return datasheet

    async def update(self, datasheet_id: UUID, updates: DatasheetFilter) -> Datasheet:
        await self.datasheet_service.update(updates, DatasheetFilter(id=datasheet_id))
        return await self.datasheet_service.find_by_id(datasheet_id)

    async def delete_by_id(self, datasheet_id: UUID) -> None:
        await self.datasheet_element_service.delete_by(
            DatasheetElementFilter(datasheet_id=datasheet_id)
        )
        await self.datasheet_service.delete_by_id(datasheet_id)
