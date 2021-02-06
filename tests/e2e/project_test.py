import pytest
from expert_dollup.app.dtos import *
from ..fixtures import *


@pytest.fixture
async def project(ac, expert_dollup_simple_project):
    fake_db = expert_dollup_simple_project
    project = ProjectDtoFactory(project_def_id=fake_db.project_definitions[0].id)
    response = await ac.post("/api/project", data=project.json())
    assert response.status_code == 200
    assert ProjectDto(**response.json()) == project
    yield project


def over_tree(tree: ProjectContainerTreeDto):
    from collections import deque

    bucket = deque(iter(tree.roots))

    while len(bucket) > 0:
        node = bucket.popleft()
        yield node
        bucket.extend(node.children)


@pytest.mark.asyncio
async def test_project_loading(ac, expert_dollup_simple_project, project):
    fake_db = expert_dollup_simple_project

    response = await ac.get(f"/api/project/{project.id}/containers")
    assert response.status_code == 200

    project_container_tree = unwrap(response, ProjectContainerTreeDto)
    expected_definition_ids = {
        definition.id
        for definition in fake_db.project_definition_containers
        if definition.instanciate_by_default
    }

    for node in over_tree(project_container_tree):
        assert node.definition.id == node.container.type_id
        expected_definition_ids.remove(node.definition.id)

    assert expected_definition_ids == set()


class FlowRunner:
    def __init__(self):
        self.steps = []

    def step(self, func):
        self.steps.append(func)
        return self

    async def run(self, *args):
        params = args

        for step in self.steps:
            params = step(*params)


@pytest.mark.asyncio
async def test_mutate_project_field(ac, expert_dollup_simple_project, project):
    response = await ac.get(f"/api/project/{project.id}/containers?level=0")
    assert response.status_code == 200, response.text

    first_layer_tree = unwrap(response, ProjectContainerTreeDto)
    assert len(field_layer_tree.roots) > 0

    response = await ac.get(
        f"/api/project/{project.id}/containers?level=4&path={first_layer_tree.roots[0].container.id}"
    )
    assert response.status_code == 200, response.text

    field_layer_tree = unwrap(response, ProjectContainerTreeDto)
    assert len(field_layer_tree.roots) > 0

    target_field = next(
        field
        for field in field_layer_tree.roots
        if field.definition.value_type == "INT"
    )
    assert isinstance(target_field.container.value["value"], int)

    expected_value = {"value": target_field.container.value["value"] + 10}
    response = await ac.put(
        f"/api/project/{project.id}/container/{target_field.container.id}/value",
        data=jsonify(expected_value),
    )
    assert response.status_code == 200, response.text

    response = await ac.get(
        f"/api/project/{project.id}/container/{target_field.container.id}"
    )
    assert response.status_code == 200, response.text

    actual_container = unwrap(response, ProjectContainerDto)
    assert actual_container.value == expected_value


def test_instanciate_collection():
    pass
    # response = await ac.post(f"/api/project/{project.id}/container")


def test_clone_collection():
    pass
    # response = await ac.post(f"/api/project/{project.id}/container/{}/clone")


def test_remove_collection():
    pass


def test_remove_project():
    pass


def test_clone_project():
    pass
    # response = await ac.post(f"/api/project/{project.id}/clone")
