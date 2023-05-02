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

    async def find(self, datasheet_id: UUID) -> Datasheet:
        return await self.db_context.find(Datasheet, datasheet_id)

    async def add(self, datasheet: Datasheet, user: User) -> Datasheet:
        ressource = authorization_factory.allow_access_to(datasheet, user)
        await self.db_context.insert(Ressource, ressource)
        await self.db_context.insert(Datasheet, datasheet)

    async def delete(self, datasheet_id: UUID) -> None:
        await self.db_context.delete_by(
            DatasheetElement, DatasheetElementFilter(datasheet_id=datasheet_id)
        )
        await self.db_context.delete(Datasheet, datasheet_id)

    async def clone(self, target: CloningDatasheet, user: User):
        datasheet = await self.find(target.target_datasheet_id)
        cloned_datasheet = Datasheet(
            id=uuid4(),
            project_definition_id=datasheet.project_definition_id,
            abstract_collection_id=datasheet.abstract_collection_id,
            name=target.clone_name,
            from_datasheet_id=datasheet.id,
            attributes_schema=datasheet.attributes_schema,
            instances_schema=datasheet.instances_schema,
            creation_date_utc=self.clock.utcnow(),
        )

        query_filter = DatasheetElementFilter(datasheet_id=target.target_datasheet_id)
        page = await self.datasheet_element_paginator.find_page(query_filter, 500)
        cloned_elements: List[DatasheetElement] = [
            DatasheetElement(
                id=uuid4(),
                datasheet_id=cloned_datasheet.id,
                aggregate_id=result.aggregate_id,
                ordinal=result.ordinal,
                attributes=result.attributes,
                original_datasheet_id=result.original_datasheet_id,
                original_owner_organization_id=user.organization_id,
                creation_date_utc=self.clock.utcnow(),
            )
            for result in page.results
        ]

        while len(page.results) == page.limit:
            page = await self.datasheet_element_paginator.find_page(
                query_filter, page.limit, page.next_page_token
            )
            cloned_elements.extend(
                DatasheetElement(
                    id=uuid4(),
                    datasheet_id=cloned_datasheet.id,
                    aggregate_id=result.aggregate_id,
                    ordinal=result.ordinal,
                    attributes=result.attributes,
                    original_datasheet_id=result.original_datasheet_id,
                    original_owner_organization_id=user.organization_id,
                    creation_date_utc=self.clock.utcnow(),
                )
                for result in page.results
            )

        await self.add(cloned_datasheet, user)
        await self.db_context.inserts(DatasheetElement, cloned_elements)
        return cloned_datasheet

    async def add_filled_datasheet(
        self, new_datasheet: NewDatasheet, user: User
    ) -> Datasheet:
        collection = await self.db_context.find(
            AggregateCollection, new_datasheet.abstract_collection_id
        )
        aggregates = await self.db_context.find_by(
            Aggregate,
            AggregateFilter(
                project_definition_id=new_datasheet.project_definition_id,
                collection_id=new_datasheet.abstract_collection_id,
            ),
        )
        datasheet = self._make_datasheet(collection, aggregates, new_datasheet)
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
        await self.db_context.inserts(DatasheetElement, elements)
        return datasheet

    def _make_datasheet(
        self,
        collection: AggregateCollection,
        aggregates: List[Aggregate],
        new_datasheet: NewDatasheet,
    ) -> Datasheet:
        datasheet_id = uuid4()
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
                        id: attribute for id, attribute in aggregate.attributes.items()
                    },
                )
                for aggregate in aggregates
            },
            creation_date_utc=self.clock.utcnow(),
        )

        return datasheet
