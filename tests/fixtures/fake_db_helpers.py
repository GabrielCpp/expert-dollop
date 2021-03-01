from enum import Enum
from typing import List
from pydantic import BaseModel, Field
from databases import Database
from os.path import join
from injector import inject
from expert_dollup.infra.expert_dollup_db import *
from expert_dollup.infra.services import *


class FakeExpertDollupDb(BaseModel):
    project_definition_containers: List[ProjectDefinitionContainerDao] = Field(
        default_factory=list
    )
    project_definitions: List[ProjectDefinitionDao] = Field(default_factory=list)
    datasheet_definitions: List[DatasheetDefinitionDao] = Field(default_factory=list)
    datasheet_definition_elements: List[DatasheetDefinitionElementDao] = Field(
        default_factory=list
    )
    label_collections: List[LabelCollectionDao] = Field(default_factory=list)
    labels: List[LabelDao] = Field(default_factory=list)
    translations: List[TranslationDao] = Field(default_factory=list)


async def populate_db(db, table, daos: Dict[str, BaseModel]):
    await db.execute_many(table.insert(), [dao.dict() for dao in daos.values()])


@inject
class DbSetupHelper:
    def __init__(
        self,
        project_definition_container_service: ProjectDefinitionContainerService,
        project_definition_service: ProjectDefinitionService,
        translation_service: TranslationService,
        datasheet_definition_service: DatasheetDefinitionService,
        datasheet_definition_element_service: DatasheetDefinitionElementService,
        label_collection_service: LabelCollectionService,
        label_service: LabelService,
    ):
        self.project_definition_container_service = project_definition_container_service
        self.project_definition_service = project_definition_service
        self.translation_service = translation_service
        self.datasheet_definition_service = datasheet_definition_service
        self.datasheet_definition_element_service = datasheet_definition_element_service
        self.label_collection_service = label_collection_service
        self.label_service = label_service

    async def init_db(self, fake_db: FakeExpertDollupDb):
        await self.project_definition_service.insert_many_raw(
            fake_db.project_definitions
        )

        await self.project_definition_container_service.insert_many_raw(
            fake_db.project_definition_containers,
        )

        await self.translation_service.insert_many_raw(fake_db.translations)
        await self.datasheet_definition_service.insert_many_raw(
            fake_db.datasheet_definitions
        )
        await self.datasheet_definition_element_service.insert_many_raw(
            fake_db.datasheet_definition_elements
        )
        await self.label_collection_service.insert_many_raw(fake_db.label_collections)
        await self.label_service.insert_many_raw(fake_db.labels)
