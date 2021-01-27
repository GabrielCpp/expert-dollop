import pytest
from .fixtures import load_fixture, ExpertDollupDbFixture, map_dao_to_dto
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *


@pytest.mark.asyncio
async def test_project_creation(ac, map_dao_to_dto):
    db = load_fixture(ExpertDollupDbFixture.SimpleProject)

    for project_definiton in db.project_definitions:
        response = await ac.post(
            "/api/project_definition", data=project_definiton.json()
        )
        assert response.status_code == 200, response.json()

    project_definition_containers_dto = map_dao_to_dto(
        db.project_definition_container,
        ProjectDefinitionContainerDao,
        ProjectDefinitionContainer,
        ProjectDefinitionContainerDto,
    )

    for project_definiton_container_dto in project_definition_containers_dto:
        response = await ac.post(
            "/api/project_definition_container",
            data=project_definiton_container_dto.json(),
        )
        assert response.status_code == 200, response.json()

    # ac.get("/project_definition")