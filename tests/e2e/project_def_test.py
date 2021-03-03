import pytest
from ..fixtures import (
    DbSetupHelper,
    map_dao_to_dto,
    normalize_request_results,
    normalize_dtos,
    SimpleProject,
)
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *


@pytest.mark.asyncio
async def test_project_creation(ac, map_dao_to_dto):
    db = SimpleProject().generate().model

    assert len(db.project_definitions) == 1
    project_definition = db.project_definitions[0]

    response = await ac.post("/api/project_definition", data=project_definition.json())
    assert response.status_code == 200, response.json()

    project_definition_containers_dto = map_dao_to_dto(
        db.project_definition_containers,
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

    containers = await AsyncCursor.all(
        ac,
        f"/api/{project_definition.id}/project_definition_containers",
        after=normalize_request_results(ProjectDefinitionContainerDto, "id"),
    )

    expected_containers = normalize_dtos(project_definition_containers_dto, "id")

    assert len(containers) == len(project_definition_containers_dto)
    assert containers == expected_containers
