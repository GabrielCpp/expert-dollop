from enum import Enum
from typing import List
from pydantic import BaseModel
from databases import Database
from os.path import join
from expert_dollup.infra.expert_dollup_db import (
    ProjectDefinitionDao,
    ProjectDefinitionContainerDao,
    project_definition_table,
    project_definition_container_table,
)


class expert_dollupDbFixture(Enum):
    SimpleProject = "simple_project_definition.json"


class Fakeexpert_dollupDb(BaseModel):
    project_container_definitions: List[ProjectDefinitionContainerDao]
    project_definitions: List[ProjectDefinitionDao]


async def init_db(database: Database, fake_db: Fakeexpert_dollupDb):
    await database.execute(
        project_definition_table.insert(),
        [element.dict() for element in fake_db.project_definitions],
    )

    await database.execute(
        project_container_definition_table.insert(),
        [element.dict() for element in fake_db.project_container_definitions],
    )


def load_fixture(fixture: expert_dollupDbFixture) -> Fakeexpert_dollupDb:
    return Fakeexpert_dollupDb.parse_file(join(".", fixture))
