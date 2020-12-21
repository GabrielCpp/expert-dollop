import pytest
import factory
from uuid import uuid4
from predykt.app.dtos import ProjectDefinitionDto, ProjectDefinitionContainerDto


class ProjectDefinitionDtoFactory(factory.Factory):
    class Meta:
        model = ProjectDefinitionDto

    id = factory.LazyFunction(uuid4)
    name = factory.Sequence(lambda n: f"Gab{n}")
    default_datasheet_id = factory.LazyFunction(uuid4)
    plugins = []


class ProjectDefinitionContainerDtoFactory(factory.Factory):
    class Meta:
        model = ProjectDefinitionContainerDto

    id = factory.LazyFunction(uuid4)
    project_def_id = factory.LazyFunction(uuid4)
    name = factory.Sequence(lambda n: f"Container{n}")
    is_collection = False
    instanciate_by_default = True
    custom_attributes = {}
    value_type = 'INT'
    default_value = {'value': 0}
    path = []


@pytest.mark.asyncio
async def test_given_project_definition_should_be_able_to_create_delete_update(ac):
    expected_project_definition = ProjectDefinitionDtoFactory()
    response = await ac.post("/api/project_definition", data=expected_project_definition.json())
    assert response.status_code == 200

    response = await ac.get(f"/api/project_definition/{expected_project_definition.id}")
    assert response.status_code == 200

    actual = ProjectDefinitionDto(**response.json())
    assert actual == expected_project_definition

    response = await ac.delete(f"/api/project_definition/{expected_project_definition.id}")
    assert response.status_code == 200

    response = await ac.get(f"/api/project_definition/{expected_project_definition.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_given_project_definition_container_should_be_able_to_create_update_delete(ac):
    project_definition = ProjectDefinitionDtoFactory()
    expected_project_definition_container = ProjectDefinitionContainerDtoFactory(
        project_def_id=project_definition.id)

    response = await ac.post("/api/project_definition", data=project_definition.json())
    assert response.status_code == 200

    response = await ac.post("/api/project_definition_container", data=expected_project_definition_container.json())
    assert response.status_code == 200

    response = await ac.get(f"/api/project_definition_container/{expected_project_definition_container.id}")
    assert response.status_code == 200

    actual = ProjectDefinitionContainerDto(**response.json())
    assert actual == expected_project_definition_container

    response = await ac.delete(f"/api/project_definition_container/{expected_project_definition_container.id}")
    assert response.status_code == 200

    response = await ac.get(f"/api/project_definition_container/{expected_project_definition_container.id}")
    assert response.status_code == 404
