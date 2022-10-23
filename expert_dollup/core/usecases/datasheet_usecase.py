from typing import List
from uuid import UUID, uuid4
from expert_dollup.shared.database_services import *
from expert_dollup.shared.starlette_injection import Clock
from expert_dollup.core.utils import authorization_factory
from expert_dollup.core.domains import *


class DatasheetUseCase:
    def __init__(
        self,
        datasheet_element_paginator: Paginator[DatasheetElement],
        db_context: DatabaseContext,
        clock: Clock,
    ):

        self.datasheet_element_paginator = datasheet_element_paginator
        self.db_context = db_context
        self.clock = clock

    async def find_by_id(self, datasheet_id: UUID) -> Datasheet:
        return await self.db_context.find_by_id(Datasheet, datasheet_id)

    async def add(self, datasheet: Datasheet, user: User) -> Datasheet:
        ressource = authorization_factory.allow_access_to(datasheet, user)
        await self.db_context.insert(Ressource, ressource)
        await self.db_context.insert(Datasheet, datasheet)

    async def delete_by_id(self, datasheet_id: UUID) -> None:
        await self.db_context.delete_by(
            DatasheetElement, DatasheetElementFilter(datasheet_id=datasheet_id)
        )
        await self.db_context.delete_by_id(Datasheet, datasheet_id)

    async def clone(self, target: CloningDatasheet, user: User):
        datasheet = await self.db_context.find_by_id(
            Datasheet, target.target_datasheet_id
        )
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
        await self.db_context.insert_many(DatasheetElement, cloned_elements)
        return cloned_datasheet

    async def add_filled_datasheet(
        self, new_datasheet: NewDatasheet, user: User
    ) -> Datasheet:
        datasheet_id = uuid4()
        collection = await self.db_context.find_by_id(
            AggregateCollection, new_datasheet.abstract_collection_id
        )
        aggregates = await self.db_context.find_by(
            Aggregate,
            AggregateFilter(
                project_definition_id=new_datasheet.project_definition_id,
                collection_id=new_datasheet.abstract_collection_id,
            ),
        )

        datasheet = Datasheet(
            id=datasheet_id,
            project_definition_id=new_datasheet.project_definition_id,
            abstract_collection_id=new_datasheet.abstract_collection_id,
            name=new_datasheet.name,
            from_datasheet_id=datasheet_id,
            attributes_schema=collection.attributes_schema,
            instances_schema={
                aggregate.id: InstanceSchema(
                    is_extendable=aggregate.is_extendable,
                    attributes_schema={
                        attribute.name: InstanceAttributeSchema(
                            is_readonly=attribute.is_readonly
                        )
                        for attribute in aggregate.attributes.values()
                    },
                )
                for aggregate in aggregates
            },
            creation_date_utc=self.clock.utcnow(),
        )
        elements = [
            DatasheetElement(
                id=uuid4(),
                datasheet_id=datasheet.id,
                aggregate_id=aggregate.id,
                ordinal=0,
                attributes=[
                    Attribute(name=attribute.name, value=attribute.value)
                    for attribute in aggregate.attributes.values()
                ],
                original_datasheet_id=datasheet.id,
                original_owner_organization_id=user.organization_id,
                creation_date_utc=self.clock.utcnow(),
            )
            for aggregate in aggregates
        ]

        await self.add(datasheet, user)
        await self.db_context.insert_many(DatasheetElement, elements)
        return datasheet
