import pytest
from typing import List
from uuid import UUID
from expert_dollup.app.dtos import *
from ..fixtures import *


async def create_project(ac, fake_db: FakeDb):
    new_project = NewProjectDetailsDtoFactory(
        project_definition_id=fake_db.get_only_one(ProjectDefinition).id
    )
    response = await ac.post("/api/project", data=new_project.json())
    assert response.status_code == 200
    project = ProjectDetailsDto.parse_obj(response.json())
    return project


async def get_containers_by_type(
    ac, project_id: UUID, type_id: UUID
) -> List[ProjectNodeDto]:
    response = await ac.get(f"/api/project/{project_id}/containers?typeId={type_id}")
    assert response.status_code == 200, response.text

    nodes = unwrap_many(response, ProjectNodeDto)
    assert len(nodes) >= 1
    return nodes[0]


async def get_node_meta(ac, project_id: UUID, type_id: UUID) -> ProjectNodeMetaDto:
    response = await ac.get(f"/api/project/{project_id}/node_meta/{type_id}")
    assert response.status_code == 200, response.text

    meta = unwrap(response, ProjectNodeMetaDto)
    return meta


@pytest.mark.asyncio
async def test_project_with_trigger(ac, db_helper: DbFixtureHelper):
    runner = FlowRunner()
    fake_db = await db_helper.load_fixtures(SuperUser(), ProjectWithTrigger())
    await ac.login_super_user()
    project = await create_project(ac, fake_db)

    checkbox_node = next(
        node_def
        for node_def in fake_db.all(ProjectDefinitionNode)
        if isinstance(node_def.field_details, BoolFieldConfig)
    )

    textbox_node = next(
        node_def
        for node_def in fake_db.all(ProjectDefinitionNode)
        if isinstance(node_def.field_details, StringFieldConfig)
    )

    root_b_node = next(
        node_def
        for node_def in fake_db.all(ProjectDefinitionNode)
        if node_def.name == "root_b"
    )

    @runner.step
    async def project_checkbox_toogle_visibility_root_collection():
        actual_node = await get_containers_by_type(ac, project.id, checkbox_node.id)
        assert actual_node.value.enabled is False, "The bool field must start unchecked"

        meta = await get_node_meta(ac, project.id, root_b_node.id)
        assert (
            meta.state.is_visible is False
        ), "root_b must be hidden because it a root collection"

        expected_value = BoolFieldValueDto(enabled=True)
        response = await ac.put(
            f"/api/project/{project.id}/container/{actual_node.id}/value",
            data=expected_value.json(),
        )
        assert response.status_code == 200, response.text

        actual_node = await get_containers_by_type(ac, project.id, checkbox_node.id)
        assert actual_node.value.enabled is True, "The bool field must en up checked"

        meta = await get_node_meta(ac, project.id, root_b_node.id)
        assert (
            meta.state.is_visible is True
        ), "Trigger must have change visitibility state of root_b"

    @runner.step
    async def _create_new_collection():
        response = await ac.post(
            f"/api/project/{project.id}/container/collection",
            data=ProjectNodeCollectionTargetDto(
                parent_node_id=None, collection_type_id=root_b_node.id
            ).json(),
        )
        assert response.status_code == 200, response.text

        root_section_name_field = await get_containers_by_type(
            ac, project.id, textbox_node.id
        )
        root_section = await get_containers_by_type(ac, project.id, root_b_node.id)
        assert root_section_name_field.value.text == root_section.label

        return (root_section_name_field,)

    @runner.step
    async def test_project_textfield_trigger_root_name_update(root_section_name_field):
        expected_value = StringFieldValueDto(text="this is my new name")
        response = await ac.put(
            f"/api/project/{project.id}/container/{root_section_name_field.id}/value",
            data=expected_value.json(),
        )
        assert response.status_code == 200, response.text

        root_section = await get_containers_by_type(ac, project.id, root_b_node.id)
        assert root_section.label == expected_value.text

    @runner.step
    async def _create_new_collection2():
        response = await ac.post(
            f"/api/project/{project.id}/container/collection",
            data=ProjectNodeCollectionTargetDto(
                parent_node_id=None, collection_type_id=root_b_node.id
            ).json(),
        )
        assert response.status_code == 200, response.text

    await runner.run()
