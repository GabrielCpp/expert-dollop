import pytest
from ..fixtures import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *


@pytest.mark.asyncio
async def test_project_creation(ac, mapper):
    db = SimpleProject().generate().model

    assert len(db.project_definitions) == 1
    project_definition = db.project_definitions[0]

    response = await ac.post(
        "/api/project_definition", data=jsonify(project_definition)
    )
    assert response.status_code == 200, response.json()

    project_definition_nodes_dto = mapper.map_many(
        db.project_definition_nodes,
        ProjectDefinitionNodeDto,
        ProjectDefinitionNode,
    )

    for project_definiton_container_dto in project_definition_nodes_dto:
        response = await ac.post(
            "/api/project_definition_node",
            data=project_definiton_container_dto.json(),
        )
        assert response.status_code == 200, response.json()

    containers = await AsyncCursor.all(
        ac,
        f"/api/{project_definition.id}/project_definition_nodes",
        after=normalize_request_results(ProjectDefinitionNodeDto, "id"),
    )

    expected_containers = normalize_dtos(project_definition_nodes_dto, "id")

    assert len(containers) == len(project_definition_nodes_dto)
    assert containers == expected_containers
