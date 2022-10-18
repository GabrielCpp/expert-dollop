from typing import List
from uuid import UUID, uuid4
from expert_dollup.shared.database_services import Page, Paginator, Repository
from expert_dollup.shared.starlette_injection import Clock
from expert_dollup.core.utils import authorization_factory
from expert_dollup.core.domains import *


class DatasheetUseCase:
    def __init__(
        self,
        ressource_service: Repository[Ressource],
        datasheet_service: Repository[Datasheet],
        datasheet_element_service: Repository[DatasheetElement],
        datasheet_element_paginator: Paginator[DatasheetElement],
        clock: Clock,
    ):
        self.ressource_service = ressource_service
        self.datasheet_service = datasheet_service
        self.datasheet_element_service = datasheet_element_service
        self.datasheet_element_paginator = datasheet_element_paginator
        self.clock = clock

    async def find_by_id(self, datasheet_id: UUID) -> Datasheet:
        return await self.datasheet_service.find_by_id(datasheet_id)

    async def clone(self, target: CloningDatasheet, user: User):
        datasheet = await self.datasheet_service.find_by_id(target.target_datasheet_id)
        cloned_datasheet = Datasheet(
            id=uuid4(),
            name=datasheet.name,
            is_staged=datasheet.is_staged,
            project_definition_id=datasheet.project_definition_id,
            from_datasheet_id=target.target_datasheet_id,
            creation_date_utc=self.clock.utcnow(),
        )

        page = Page[DatasheetElement]()
        cloned_elements: List[DatasheetElement] = []

        while len(page.results) == page.limit:
            page = await self.datasheet_element_paginator.find_page(
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
                        element_def_id=result.element_def_id,
                        child_element_reference=uuid4(),
                        ordinal=result.ordinal,
                        properties=result.properties,
                        original_datasheet_id=result.original_datasheet_id,
                        original_owner_organization_id=user.organization_id,
                        creation_date_utc=self.clock.utcnow(),
                    )
                    for result in page.results
                ]
            )

        cloned_datasheet = Datasheet(
            id=uuid4(),
            name=datasheet_clone_target.clone_name,
            is_staged=datasheet.is_staged,
            project_definition_id=datasheet.project_definition_id,
            from_datasheet_id=datasheet.from_datasheet_id,
            creation_date_utc=self.clock.utcnow(),
        )

        await self.add(cloned_datasheet, user)
        await self.datasheet_element_service.insert_many(cloned_elements)

        return cloned_datasheet

    async def add(self, datasheet: Datasheet, user: User) -> Datasheet:
        await self.ressource_service.insert(
            authorization_factory.allow_access_to(datasheet, user)
        )
        await self.datasheet_service.insert(datasheet)

    async def add_filled_datasheet(self, datasheet: Datasheet, user: User) -> Datasheet:
        await self.ressource_service.insert(
            authorization_factory.allow_access_to(datasheet, user)
        )
        await self.datasheet_service.insert(datasheet)
        definition_elements = await self.datasheet_definition_element_service.find_by(
            DatasheetDefinitionElementFilter(
                project_definition_id=datasheet.project_definition_id
            )
        )

        elements = [
            DatasheetElement(
                datasheet_id=datasheet.id,
                element_def_id=definition_element.id,
                child_element_reference=uuid4(),
                ordinal=0,
                properties={
                    name: default_property.value
                    for name, default_property in definition_element.default_properties.items()
                },
                original_datasheet_id=datasheet.id,
                original_owner_organization_id=user.organization_id,
                creation_date_utc=self.clock.utcnow(),
            )
            for definition_element in definition_elements
        ]

        await self.datasheet_element_service.insert_many(elements)
        return datasheet

    async def delete_by_id(self, datasheet_id: UUID) -> None:
        await self.datasheet_element_service.delete_by(
            DatasheetElementFilter(datasheet_id=datasheet_id)
        )
        await self.datasheet_service.delete_by_id(datasheet_id)
