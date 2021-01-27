from enum import Enum
from typing import List
from pydantic import BaseModel
from databases import Database
from os.path import join
from .mapping_helpers import map_dao_to_dto
from expert_dollup.infra.expert_dollup_db import (
    ProjectDefinitionDao,
    ProjectDefinitionContainerDao,
    project_definition_table,
    project_definition_container_table,
    TranslationDao,
)


class ExpertDollupDbFixture(Enum):
    SimpleProject = "simple_project_definition.json"

    def __str__(self):
        return self.value


class FakeExpertDollupDb(BaseModel):
    project_definition_container: List[ProjectDefinitionContainerDao]
    project_definitions: List[ProjectDefinitionDao]
    translations: List[TranslationDao]


async def init_db(database: Database, fake_db: FakeExpertDollupDb):
    await database.execute(
        project_definition_table.insert(),
        [element.dict() for element in fake_db.project_definitions],
    )

    await database.execute(
        project_container_definition_table.insert(),
        [element.dict() for element in fake_db.project_definition_container],
    )


def load_fixture(fixture: ExpertDollupDbFixture) -> FakeExpertDollupDb:
    return FakeExpertDollupDb.parse_file(join(".", "tests", "fixtures", str(fixture)))
