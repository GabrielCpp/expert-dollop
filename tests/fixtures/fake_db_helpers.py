from enum import Enum
from typing import List
from pydantic import BaseModel
from databases import Database
from os.path import join
from expert_dollup.infra.expert_dollup_db import *


class ExpertDollupDbFixture(Enum):
    SimpleProject = "simple_project_definition.json"

    def __str__(self):
        return self.value


class FakeExpertDollupDb(BaseModel):
    project_definition_containers: List[ProjectDefinitionContainerDao]
    project_definitions: List[ProjectDefinitionDao]
    translations: List[TranslationDao]


async def init_db(database: Database, fake_db: FakeExpertDollupDb):
    await database.execute_many(
        project_definition_table.insert(),
        [element.dict() for element in fake_db.project_definitions],
    )

    await database.execute_many(
        project_definition_container_table.insert(),
        [element.dict() for element in fake_db.project_definition_containers],
    )

    await database.execute_many(
        translation_table.insert(),
        [element.dict() for element in fake_db.translations],
    )


def load_fixture(fixture: ExpertDollupDbFixture) -> FakeExpertDollupDb:
    return FakeExpertDollupDb.parse_file(join(".", "tests", "fixtures", str(fixture)))
