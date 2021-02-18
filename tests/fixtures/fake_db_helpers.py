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
    ):
        self.project_definition_container_service = project_definition_container_service
        self.project_definition_service = project_definition_service
        self.translation_service = translation_service

    async def init_db(self, fake_db: FakeExpertDollupDb):
        await self.project_definition_service.insert_many_raw(
            fake_db.project_definitions
        )

        await self.project_definition_container_service.insert_many_raw(
            fake_db.project_definition_containers,
        )

        await self.translation_service.insert_many_raw(fake_db.translations)
