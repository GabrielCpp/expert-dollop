import pytest
from typing import List
from expert_dollup.app.dtos import *
from ..fixtures import *


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


async def create_project(ac, fake_db: FakeDb):
    new_project = NewProjectDetailsDtoFactory(
        project_definition_id=fake_db.get_only_one(ProjectDefinition).id
    )
    project_dto = await ac.post_json(
        "/api/projects", new_project, unwrap_with=ProjectDetailsDto
    )
    return project_dto


async def find_collection_node_to_clone(
    ac,
    project_dto: ProjectDetailsDto,
    collection_node_definition: ProjectDefinitionNode,
):
    nodes = await ac.get_json(
        f"/api/projects/{project_dto.id}/containers?typeId={collection_node_definition.id}",
        unwrap_with=List[ProjectNodeDto],
        after=make_sorter(lambda x: x.id),
    )
    assert len(nodes) == 1
    return nodes[0]


@pytest.mark.asyncio
async def test_project_loading(ac, db_helper: DbFixtureHelper):
    fake_db = await db_helper.load_fixtures(SuperUser(), SimpleProject())
    await ac.login_super_user()

    project_dto = await create_project(ac, fake_db)
    nodes = await ac.get_json(
        f"/api/projects/{project_dto.id}/children",
        unwrap_with=List[ProjectNodeDto],
        after=make_sorter(lambda d: d.type_id),
    )

    assert_valid_instance_list_for_definition(
        nodes, fake_db, IsDefinitionInstanciated()
    )


@pytest.mark.asyncio
async def test_mutate_project_field(ac, db_helper: DbFixtureHelper):
    async def get_root_level_nodes(project_dto: ProjectDetailsDto):
        tree = await ac.get_json(
            f"/api/projects/{project_dto.id}/roots", unwrap_with=ProjectNodeTreeDto
        )
        assert len(tree.roots) > 0
        return tree.roots

    async def extract_int_field_from_root_node_fields(
        project_dto: ProjectDetailsDto, roots: List[ProjectNodeTreeTypeNodeDto]
    ):
        fields = await ac.get_json(
            f"/api/projects/{project_dto.id}/children?level=4&path={roots[0].nodes[0].node.id}",
            unwrap_with=List[ProjectNodeDto],
        )
        assert len(fields) > 0

        target_field_dto = next(
            field for field in fields if hasattr(field.value, "integer")
        )
        assert isinstance(target_field_dto.value.integer, int)

        return target_field_dto

    async def mutate_target_field_by_value_increment(
        project_dto: ProjectDetailsDto, target_field_dto
    ):
        expected_value = IntFieldValueDto(integer=target_field_dto.value.integer + 10)
        await ac.put_json(
            f"/api/projects/{project_dto.id}/container/{target_field_dto.id}/value",
            expected_value,
        )

        actual_node = await ac.get_json(
            f"/api/projects/{project_dto.id}/container/{target_field_dto.id}",
            unwrap_with=ProjectNodeDto,
        )

        assert actual_node.value == expected_value

    fake_db = await db_helper.load_fixtures(SuperUser(), SimpleProject())
    await ac.login_super_user()

    project_dto = await create_project(ac, fake_db)
    roots = await get_root_level_nodes(project_dto)
    target_field_dto = await extract_int_field_from_root_node_fields(project_dto, roots)
    await mutate_target_field_by_value_increment(project_dto, target_field_dto)


@pytest.mark.asyncio
async def test_instanciate_collection(ac, db_helper: DbFixtureHelper):
    fake_db = await db_helper.load_fixtures(SuperUser(), SimpleProject())
    await ac.login_super_user()

    root_collection_node_definition = next(
        container_definition
        for container_definition in fake_db.all(ProjectDefinitionNode)
        if container_definition.is_collection and len(container_definition.path) == 0
    )
    project_dto = await create_project(ac, fake_db)
    nodes = await ac.post_json(
        f"/api/projects/{project_dto.id}/container/collection",
        ProjectNodeCollectionTargetDto(
            collection_type_id=root_collection_node_definition.id,
        ),
        unwrap_with=List[ProjectNodeDto],
        after=make_sorter(lambda x: (len(x.path), x.path)),
    )

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

    async def clone_collection_node(
        project_dto: ProjectDetailsDto, node_dto: ProjectNodeDto
    ):
        cloned_node_dtos = await ac.post_json(
            f"/api/projects/{project_dto.id}/container/{node_dto.id}/clone",
            unwrap_with=List[ProjectNodeDto],
            after=make_sorter(lambda x: (len(x.type_path), x.type_path, x.type_name)),
        )
        return cloned_node_dtos

    async def ensure_original_node_subtree_is_equivalent_to_new_one(
        project_dto: ProjectDetailsDto,
        node_dto: ProjectNodeDto,
        cloned_node_dtos: List[ProjectNodeDto],
    ):
        original_nodes = await ac.get_json(
            f"/api/projects/{project_dto.id}/subtree?{'&'.join('path=' + str(item) for item in [*node_dto.path, node_dto.id])}",
            unwrap_with=List[ProjectNodeDto],
            after=make_sorter(lambda x: (len(x.type_path), x.type_path, x.type_name)),
        )
        assert_clone_tree_is_equivalent(cloned_node_dtos, original_nodes)

    fake_db = await db_helper.load_fixtures(SuperUser(), SimpleProject())
    await ac.login_super_user()

    collection_node_definition = next(
        container_definition
        for container_definition in fake_db.all(ProjectDefinitionNode)
        if container_definition.is_collection
        and container_definition.instanciate_by_default
        and len(container_definition.path) == 1
    )
    project_dto = await create_project(ac, fake_db)
    collection_node_dto = await find_collection_node_to_clone(
        ac, project_dto, collection_node_definition
    )
    cloned_node_dtos = await clone_collection_node(project_dto, collection_node_dto)
    await ensure_original_node_subtree_is_equivalent_to_new_one(
        project_dto, collection_node_dto, cloned_node_dtos
    )


@pytest.mark.asyncio
async def test_remove_collection(ac, db_helper: DbFixtureHelper):
    async def delete_collection_instance(
        project_dto: ProjectDetailsDto, collection_node_dto: ProjectNodeDto
    ):
        await ac.delete_json(
            f"/api/projects/{project_dto.id}/container/{collection_node_dto.id}"
        )

    async def check_that_collection_was_effectively_deleted(
        project_dto: ProjectDetailsDto, collection_node_dto: ProjectNodeDto
    ):
        await ac.get_json(
            f"/api/projects/{project_dto.id}/container/{collection_node_dto.id}",
            expected_status_code=404,
        )

        query_path = "&".join(
            f"path={item}"
            for item in [*collection_node_dto.path, collection_node_dto.id]
        )
        nodes = await ac.get_json(
            f"/api/projects/{project_dto.id}/children?{query_path}",
            unwrap_with=List[ProjectNodeDto],
            after=make_sorter(lambda x: x.id),
        )
        assert nodes == []

    fake_db = await db_helper.load_fixtures(
        SuperUser(), SimpleProject(), GrantRessourcePermissions()
    )
    await ac.login_super_user()

    collection_node_definition = next(
        container_definition
        for container_definition in fake_db.all(ProjectDefinitionNode)
        if container_definition.is_collection
        and container_definition.instanciate_by_default
        and len(container_definition.path) == 1
    )
    project_dto = await create_project(ac, fake_db)
    collection_node_dto = await find_collection_node_to_clone(
        ac, project_dto, collection_node_definition
    )
    await delete_collection_instance(project_dto, collection_node_dto)
    await check_that_collection_was_effectively_deleted(
        project_dto, collection_node_dto
    )


@pytest.mark.asyncio
async def test_remove_project(ac, db_helper: DbFixtureHelper):
    fake_db = await db_helper.load_fixtures(SuperUser(), SimpleProject())
    await ac.login_super_user()

    project_dto = await create_project(ac, fake_db)
    await ac.delete_json(f"/api/projects/{project_dto.id}")
    await ac.get_json(f"/api/projects/{project_dto.id}", expected_status_code=404)


@pytest.mark.asyncio
async def test_clone_project(ac, db_helper: DbFixtureHelper):
    fake_db = await db_helper.load_fixtures(SuperUser(), SimpleProject())
    await ac.login_super_user()

    project_dto = await create_project(ac, fake_db)
    cloned_project_dto = await ac.post_json(
        f"/api/projects/{project_dto.id}/clone", unwrap_with=ProjectDetailsDto
    )
    assert cloned_project_dto.id != project_dto.id

    atual_cloned_project_dto = await ac.get_json(
        f"/api/projects/{cloned_project_dto.id}", unwrap_with=ProjectDetailsDto
    )
    assert atual_cloned_project_dto == cloned_project_dto

    # TODO: Check result project have same content than before
