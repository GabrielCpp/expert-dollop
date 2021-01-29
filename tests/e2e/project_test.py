import pytest
from expert_dollup.app.dtos import ProjectDto
from ..fixtures import *


@pytest.mark.asyncio
async def test_project_loading(ac, dal):
    fake_db = load_fixture(ExpertDollupDbFixture.SimpleProject)
    await init_db(dal, fake_db)

    project = ProjectDtoFactory(project_def_id=fake_db.project_definitions[0].id)
    response = await ac.post("/api/project", data=project.json())
    assert response.status_code == 200


def test_mutate_project_field():
    pass


def test_instanciate_collection():
    pass


def test_clone_collection():
    pass


def test_remove_collection():
    pass
