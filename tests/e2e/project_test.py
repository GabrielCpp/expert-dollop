import pytest
from expert_dollup.app.dtos import ProjectDto
from ..fixtures import *


@pytest.mark.asyncio
async def test_project_loading(ac, expert_dollup_simple_project):
    fake_db = expert_dollup_simple_project
    project = ProjectDtoFactory(project_def_id=fake_db.project_definitions[0].id)
    response = await ac.post("/api/project", data=project.json())
    assert response.status_code == 200
    assert ProjectDto(**response.json()) == project

    response = await ac.get(f"/api/project/{project.id}/containers")
    assert response.status_code == 200
    print(response.json())
    assert len(response.json()["roots"]) == 2


def test_mutate_project_field():
    pass


def test_instanciate_collection():
    pass


def test_clone_collection():
    pass


def test_remove_collection():
    pass


def test_remove_project():
    pass


def test_clone_project():
    pass
