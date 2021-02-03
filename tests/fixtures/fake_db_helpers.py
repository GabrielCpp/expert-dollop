from enum import Enum
from typing import List
from pydantic import BaseModel
from databases import Database
from os.path import join
from injector import inject
from expert_dollup.infra.expert_dollup_db import *
from expert_dollup.infra.services import *


class ExpertDollupDbFixture(Enum):
    SimpleProject = "simple_project_definition.json"

    def __str__(self):
        return self.value


class FakeExpertDollupDb(BaseModel):
    project_definition_containers: List[ProjectDefinitionContainerDao]
    project_definitions: List[ProjectDefinitionDao]
    translations: List[TranslationDao]


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

    @staticmethod
    def load_fixture(fixture: ExpertDollupDbFixture) -> FakeExpertDollupDb:
        return FakeExpertDollupDb.parse_file(
            join(".", "tests", "fixtures", str(fixture))
        )
