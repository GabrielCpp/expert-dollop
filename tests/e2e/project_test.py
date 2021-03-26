import pytest
from typing import List
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


def assert_valid_tree_for_definition(tree, fake_db, predicate):
    expected_definition_ids = {
        definition.id
        for definition in sorted(
            fake_db.project_definition_nodes,
            key=lambda d: (len(d.path), d.id),
        )
        if predicate(definition)
    }

    for node in over_tree(tree):
        assert node.definition.id == node.container.type_id
        expected_definition_ids.remove(node.definition.id)

    assert expected_definition_ids == set()


@pytest.mark.asyncio
async def test_project_loading(ac, expert_dollup_simple_project, project):
    class IsDefinitionInstanciated:
        def __init__(self):
            self.disqualifying_parent = set()

        def __call__(self, definition) -> bool:
            if definition.instanciate_by_default:
                return not any(
                    str(parent_id) in definition.path
                    for parent_id in self.disqualifying_parent
                )

            self.disqualifying_parent.add(definition.id)
            return False

    fake_db = expert_dollup_simple_project

    response = await ac.get(f"/api/project/{project.id}/children")
    assert response.status_code == 200

    project_container_tree = unwrap(response, ProjectContainerTreeDto)
    assert_valid_tree_for_definition(
        project_container_tree, fake_db, IsDefinitionInstanciated()
    )


@pytest.mark.asyncio
async def test_mutate_project_field(ac, expert_dollup_simple_project, project):
    runner = FlowRunner()

    @runner.step
    async def get_root_level_containers():
        response = await ac.get(f"/api/project/{project.id}/children?level=0")
        assert response.status_code == 200, response.text

        first_layer_tree = unwrap(response, ProjectContainerTreeDto)
        assert len(first_layer_tree.roots) > 0

        return (first_layer_tree,)

    @runner.step
    async def extract_int_field_from_root_container_fields(first_layer_tree):
        response = await ac.get(
            f"/api/project/{project.id}/children?level=4&path={first_layer_tree.roots[0].container.id}"
        )
        assert response.status_code == 200, response.text

        field_layer_tree = unwrap(response, ProjectContainerTreeDto)
        assert len(field_layer_tree.roots) > 0

        target_field = next(
            field
            for field in field_layer_tree.roots
            if field.definition.value_type == "INT"
        )
        assert isinstance(target_field.container.value.integer, int)

        return (target_field,)

    @runner.step
    async def mutate_target_field_by_value_increment(target_field):
        expected_value = IntFieldValueDto(
            integer=target_field.container.value.integer + 10
        )
        response = await ac.put(
            f"/api/project/{project.id}/container/{target_field.container.id}/value",
            data=expected_value.json(),
        )
        assert response.status_code == 200, response.text

        return (target_field, expected_value)

    @runner.step
    async def check_value_mutation_can_be_retrieved(target_field, expected_value):
        response = await ac.get(
            f"/api/project/{project.id}/container/{target_field.container.id}"
        )
        assert response.status_code == 200, response.text

        actual_container = unwrap(response, ProjectContainerDto)
        assert actual_container.value == expected_value

    await runner.run()


@pytest.mark.asyncio
async def test_instanciate_collection(ac, expert_dollup_simple_project, project):
    fake_db = expert_dollup_simple_project
    root_collection_container_definition = next(
        container_definition
        for container_definition in fake_db.project_definition_nodes
        if container_definition.is_collection and len(container_definition.path) == 0
    )

    response = await ac.post(
        f"/api/project/{project.id}/container/collection",
        data=ProjectContainerCollectionTargetDto(
            collection_type_id=root_collection_container_definition.id,
        ).json(),
    )
    assert response.status_code == 200, response.text

    collection_tree = unwrap(response, ProjectContainerTreeDto)
    assert_valid_tree_for_definition(
        collection_tree,
        fake_db,
        lambda definition: definition.id == root_collection_container_definition.id
        or str(root_collection_container_definition.id) in definition.path,
    )


@pytest.mark.asyncio
async def test_clone_collection(ac, expert_dollup_simple_project, project):
    def assert_clone_tree_is_equivalent(
        lhs_nodes: List[ProjectContainerNodeDto],
        rhs_nodes: List[ProjectContainerNodeDto],
    ):
        assert len(lhs_nodes) == len(rhs_nodes)

        for lhs_node, rhs_node in zip(lhs_nodes, rhs_nodes):
            assert lhs_node.definition == rhs_node.definition
            assert lhs_node.meta == rhs_node.meta
            assert lhs_node.container.id != rhs_node.container.id
            assert lhs_node.container.project_id == rhs_node.container.project_id
            assert lhs_node.container.type_id == rhs_node.container.type_id
            assert lhs_node.container.value == rhs_node.container.value
            assert_clone_tree_is_equivalent(lhs_node.children, rhs_node.children)

    fake_db = expert_dollup_simple_project
    runner = FlowRunner()
    collection_container_definition = next(
        container_definition
        for container_definition in fake_db.project_definition_nodes
        if container_definition.is_collection
        and container_definition.instanciate_by_default
        and len(container_definition.path) == 1
    )

    @runner.step
    async def find_container_to_clone():
        response = await ac.get(
            f"/api/project/{project.id}/containers?typeId={collection_container_definition.id}"
        )
        assert response.status_code == 200, response.text

        containers_page = unwrap(response, ProjectContainerPageDto)
        assert len(containers_page.results) == 1

        collection_container = containers_page.results[0]
        return (collection_container,)

    @runner.step
    async def clone_container(collection_container):
        response = await ac.post(
            f"/api/project/{project.id}/container/{collection_container.id}/clone"
        )
        assert response.status_code == 200, response.text

        collection_tree = unwrap(response, ProjectContainerTreeDto)
        return (collection_container, collection_tree)

    @runner.step
    async def ensure_original_container_subtree_is_equivalent_to_new_one(
        collection_container, collection_tree
    ):
        response = await ac.get(
            f"/api/project/{project.id}/container/{collection_container.id}/subtree"
        )
        assert response.status_code == 200, response.text
        original_tree = unwrap(response, ProjectContainerTreeDto)

        assert_clone_tree_is_equivalent(collection_tree.roots, original_tree.roots)

    await runner.run()


@pytest.mark.asyncio
async def test_remove_collection(ac, expert_dollup_simple_project, project):
    fake_db = expert_dollup_simple_project
    runner = FlowRunner()
    collection_container_definition = next(
        container_definition
        for container_definition in fake_db.project_definition_nodes
        if container_definition.is_collection
        and container_definition.instanciate_by_default
        and len(container_definition.path) == 1
    )

    @runner.step
    async def find_container_to_clone():
        response = await ac.get(
            f"/api/project/{project.id}/containers?typeId={collection_container_definition.id}"
        )
        assert response.status_code == 200, response.text

        containers_page = unwrap(response, ProjectContainerPageDto)
        assert len(containers_page.results) == 1

        collection_container = containers_page.results[0]
        return (collection_container,)

    @runner.step
    async def delete_collection_instance(collection_container):
        response = await ac.delete(
            f"/api/project/{project.id}/container/{collection_container.id}"
        )
        assert response.status_code == 200, response.text

        return (collection_container,)

    @runner.step
    async def check_that_collection_was_effectively_deleted(collection_container):
        response = await ac.get(
            f"/api/project/{project.id}/container/{collection_container.id}"
        )
        assert response.status_code == 404, response.text

        query_path = "&".join(
            [
                "path=" + str(item)
                for item in [*collection_container.path, collection_container.id]
            ]
        )
        response = await ac.get(f"/api/project/{project.id}/children?{query_path}")
        assert response.status_code == 200, response.text

        tree = unwrap(response, ProjectContainerTreeDto)
        assert tree.roots == []

    await runner.run()


@pytest.mark.asyncio
async def test_remove_project(ac, project):
    response = await ac.delete(f"/api/project/{project.id}")
    assert response.status_code == 200, response.text

    response = await ac.get(f"/api/project/{project.id}")
    assert response.status_code == 404, response.text


@pytest.mark.asyncio
async def test_clone_project(ac, project):
    response = await ac.post(f"/api/project/{project.id}/clone")
    assert response.status_code == 200, response.text

    cloned_project = unwrap(response, ProjectDto)
    assert cloned_project.id != project.id

    response = await ac.get(f"/api/project/{cloned_project.id}")
    assert response.status_code == 200, response.text

    # TODO: Check result project have same content than before
