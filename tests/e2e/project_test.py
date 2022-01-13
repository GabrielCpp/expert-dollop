import pytest
from typing import List
from expert_dollup.app.dtos import *
from ..fixtures import *


async def create_project(ac, fake_db: FakeDb):
    project = ProjectDetailsDtoFactory(
        project_def_id=fake_db.get_only_one(ProjectDefinition).id
    )
    response = await ac.post("/api/project", data=project.json())
    assert response.status_code == 200
    assert ProjectDetailsDto(**response.json()) == project
    return project


def over_tree(tree: ProjectNodeTreeDto):
    from collections import deque

    bucket = deque(iter(tree.roots))

    while len(bucket) > 0:
        node = bucket.popleft()
        yield node
        bucket.extend(node.children)


def assert_valid_instance_list_for_definition(nodes, fake_db: FakeDb, predicate):
    expected_definition_ids = {
        definition.id
        for definition in sorted(
            fake_db.all(ProjectDefinitionNode),
            key=lambda d: (len(d.path), d.id),
        )
        if predicate(definition)
    }

    for node in nodes:
        expected_definition_ids.remove(node.type_id)

    assert expected_definition_ids == set()


@pytest.mark.asyncio
async def test_project_loading(ac, db_helper: DbFixtureHelper):
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

    fake_db = await db_helper.load_fixtures(SimpleProject)
    project = await create_project(ac, fake_db)

    response = await ac.get(f"/api/project/{project.id}/children")
    assert response.status_code == 200

    nodes = unwrap_many(response, ProjectNodeDto, lambda d: d.type_id)
    print(nodes)
    assert_valid_instance_list_for_definition(
        nodes, fake_db, IsDefinitionInstanciated()
    )


@pytest.mark.asyncio
async def test_mutate_project_field(ac, db_helper: DbFixtureHelper):
    runner = FlowRunner()
    fake_db = await db_helper.load_fixtures(SimpleProject)
    project = await create_project(ac, fake_db)

    @runner.step
    async def get_root_level_nodes():
        response = await ac.get(f"/api/project/{project.id}/roots")
        assert response.status_code == 200, response.text

        tree = unwrap(response, ProjectNodeTreeDto)
        assert len(tree.roots) > 0

        return (tree.roots,)

    @runner.step
    async def extract_int_field_from_root_node_fields(roots):
        response = await ac.get(
            f"/api/project/{project.id}/children?level=4&path={roots[0].nodes[0].node.id}"
        )
        assert response.status_code == 200, response.text

        fields = unwrap_many(response, ProjectNodeDto)
        assert len(fields) > 0

        target_field = next(
            field for field in fields if hasattr(field.value, "integer")
        )
        assert isinstance(target_field.value.integer, int)

        return (target_field,)

    @runner.step
    async def mutate_target_field_by_value_increment(target_field):
        expected_value = IntFieldValueDto(integer=target_field.value.integer + 10)
        response = await ac.put(
            f"/api/project/{project.id}/container/{target_field.id}/value",
            data=expected_value.json(),
        )
        assert response.status_code == 200, response.text

        return (target_field, expected_value)

    @runner.step
    async def check_value_mutation_can_be_retrieved(target_field, expected_value):
        response = await ac.get(
            f"/api/project/{project.id}/container/{target_field.id}"
        )
        assert response.status_code == 200, response.text

        actual_node = unwrap(response, ProjectNodeDto)
        assert actual_node.value == expected_value

    await runner.run()


@pytest.mark.asyncio
async def test_instanciate_collection(ac, db_helper: DbFixtureHelper):
    fake_db = await db_helper.load_fixtures(SimpleProject)
    project = await create_project(ac, fake_db)
    root_collection_node_definition = next(
        container_definition
        for container_definition in fake_db.all(ProjectDefinitionNode)
        if container_definition.is_collection and len(container_definition.path) == 0
    )

    response = await ac.post(
        f"/api/project/{project.id}/container/collection",
        data=ProjectNodeCollectionTargetDto(
            collection_type_id=root_collection_node_definition.id,
        ).json(),
    )
    assert response.status_code == 200, response.text

    nodes = unwrap_many(response, ProjectNodeDto, lambda x: (len(x.path), x.path))
    assert_valid_instance_list_for_definition(
        nodes,
        fake_db,
        lambda definition: definition.id == root_collection_node_definition.id
        or str(root_collection_node_definition.id) in definition.path,
    )


@pytest.mark.asyncio
async def test_clone_collection(ac, db_helper: DbFixtureHelper):
    def assert_clone_tree_is_equivalent(
        lhs_nodes: List[ProjectNodeTreeNodeDto],
        rhs_nodes: List[ProjectNodeTreeNodeDto],
    ):
        assert len(lhs_nodes) == len(rhs_nodes)

        for lhs_node, rhs_node in zip(lhs_nodes, rhs_nodes):
            assert lhs_node.id != rhs_node.id
            assert lhs_node.project_id == rhs_node.project_id
            assert lhs_node.type_id == rhs_node.type_id
            assert lhs_node.type_path == rhs_node.type_path
            assert lhs_node.value == rhs_node.value

    fake_db = await db_helper.load_fixtures(SimpleProject)
    project = await create_project(ac, fake_db)
    runner = FlowRunner()
    collection_node_definition = next(
        container_definition
        for container_definition in fake_db.all(ProjectDefinitionNode)
        if container_definition.is_collection
        and container_definition.instanciate_by_default
        and len(container_definition.path) == 1
    )

    @runner.step
    async def find_node_to_clone():
        response = await ac.get(
            f"/api/project/{project.id}/containers?typeId={collection_node_definition.id}"
        )
        assert response.status_code == 200, response.text

        nodes = unwrap_many(response, ProjectNodeDto, lambda x: x.id)
        assert len(nodes) == 1

        collection_node = nodes[0]
        return (collection_node,)

    @runner.step
    async def clone_node(node):
        response = await ac.post(f"/api/project/{project.id}/container/{node.id}/clone")
        assert response.status_code == 200, response.text

        nodes = unwrap_many(
            response,
            ProjectNodeDto,
            lambda x: (len(x.type_path), x.type_path, x.type_name),
        )
        return (node, nodes)

    @runner.step
    async def ensure_original_node_subtree_is_equivalent_to_new_one(node, nodes):
        response = await ac.get(
            f"/api/project/{project.id}/subtree?{'&'.join('path=' + str(item) for item in [*node.path, node.id])}"
        )
        assert response.status_code == 200, response.text

        original_nodes = unwrap_many(
            response,
            ProjectNodeDto,
            lambda x: (len(x.type_path), x.type_path, x.type_name),
        )
        assert_clone_tree_is_equivalent(nodes, original_nodes)

    await runner.run()


@pytest.mark.asyncio
async def test_remove_collection(ac, db_helper: DbFixtureHelper):
    fake_db = await db_helper.load_fixtures(SimpleProject)
    project = await create_project(ac, fake_db)
    runner = FlowRunner()
    collection_node_definition = next(
        container_definition
        for container_definition in fake_db.all(ProjectDefinitionNode)
        if container_definition.is_collection
        and container_definition.instanciate_by_default
        and len(container_definition.path) == 1
    )

    @runner.step
    async def find_node_to_clone():
        response = await ac.get(
            f"/api/project/{project.id}/containers?typeId={collection_node_definition.id}"
        )
        assert response.status_code == 200, response.text

        nodes = unwrap_many(response, ProjectNodeDto, lambda x: x.id)
        assert len(nodes) == 1

        collection_node = nodes[0]
        return (collection_node,)

    @runner.step
    async def delete_collection_instance(collection_node):
        response = await ac.delete(
            f"/api/project/{project.id}/container/{collection_node.id}"
        )
        assert response.status_code == 200, response.text

        return (collection_node,)

    @runner.step
    async def check_that_collection_was_effectively_deleted(collection_node):
        response = await ac.get(
            f"/api/project/{project.id}/container/{collection_node.id}"
        )
        assert response.status_code == 404, response.text

        query_path = "&".join(
            [
                "path=" + str(item)
                for item in [*collection_node.path, collection_node.id]
            ]
        )
        response = await ac.get(f"/api/project/{project.id}/children?{query_path}")
        assert response.status_code == 200, response.text

        nodes = unwrap_many(response, ProjectNodeDto, lambda x: x.id)
        assert nodes == []

    await runner.run()


@pytest.mark.asyncio
async def test_remove_project(ac, db_helper: DbFixtureHelper):
    fake_db = await db_helper.load_fixtures(SimpleProject)
    project = await create_project(ac, fake_db)

    response = await ac.delete(f"/api/project/{project.id}")
    assert response.status_code == 200, response.text

    response = await ac.get(f"/api/project/{project.id}")
    assert response.status_code == 404, response.text


@pytest.mark.asyncio
async def test_clone_project(ac, db_helper: DbFixtureHelper):
    fake_db = await db_helper.load_fixtures(SimpleProject)
    project = await create_project(ac, fake_db)

    response = await ac.post(f"/api/project/{project.id}/clone")
    assert response.status_code == 200, response.text

    cloned_project = unwrap(response, ProjectDetailsDto)
    assert cloned_project.id != project.id

    response = await ac.get(f"/api/project/{cloned_project.id}")
    assert response.status_code == 200, response.text

    # TODO: Check result project have same content than before
