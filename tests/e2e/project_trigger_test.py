import pytest
from typing import List
from uuid import UUID
from expert_dollup.app.dtos import *
from ..fixtures import *


async def create_project(ac, fake_db: FakeDb):
    new_project = NewProjectDetailsDtoFactory(
        project_definition_id=fake_db.get_only_one(ProjectDefinition).id
    )
    response = await ac.post("/api/projects", data=new_project.json())
    assert response.status_code == 200
    project = ProjectDetailsDto.parse_obj(response.json())
    return project


async def get_containers_by_type(
    ac, project_id: UUID, type_id: UUID
) -> List[ProjectNodeDto]:
    nodes = await ac.get_json(
        f"/api/projects/{project_id}/containers?typeId={type_id}",
        unwrap_with=List[ProjectNodeDto],
    )
    assert len(nodes) >= 1
    return nodes[0]


async def get_node_meta(ac, project_id: UUID, type_id: UUID) -> ProjectNodeMetaDto:
    return await ac.get_json(
        f"/api/projects/{project_id}/node_meta/{type_id}",
        unwrap_with=ProjectNodeMetaDto,
    )


@pytest.mark.asyncio
async def test_project_with_trigger(ac, db_helper: DbFixtureHelper):
    async def project_checkbox_toogle_visibility_root_collection(
        project_dto: ProjectDetailsDto,
        root_b_node: ProjectDefinitionNode,
        checkbox_node: ProjectDefinitionNode,
    ):
        actual_node = await get_containers_by_type(ac, project_dto.id, checkbox_node.id)
        assert actual_node.value.enabled is False, "The bool field must start unchecked"

        meta = await get_node_meta(ac, project_dto.id, root_b_node.id)
        assert (
            meta.state.is_visible is False
        ), "root_b must be hidden because it a root collection"

        expected_value = BoolFieldValueDto(enabled=True)
        await ac.put_json(
            f"/api/projects/{project_dto.id}/container/{actual_node.id}/value",
            expected_value,
        )

        actual_node = await get_containers_by_type(ac, project_dto.id, checkbox_node.id)
        assert actual_node.value.enabled is True, "The bool field must en up checked"

        meta = await get_node_meta(ac, project_dto.id, root_b_node.id)
        assert (
            meta.state.is_visible is True
        ), "Trigger must have change visitibility state of root_b"

    async def create_new_collection(
        project_dto: ProjectDetailsDto,
        root_b_node: ProjectDefinitionNode,
        textbox_node: ProjectDefinitionNode,
    ):
        await ac.post_json(
            f"/api/projects/{project_dto.id}/container/collection",
            ProjectNodeCollectionTargetDto(
                parent_node_id=None, collection_type_id=root_b_node.id
            ),
        )

        root_section_name_field = await get_containers_by_type(
            ac, project_dto.id, textbox_node.id
        )
        root_section = await get_containers_by_type(ac, project_dto.id, root_b_node.id)
        assert root_section_name_field.value.text == root_section.label

        return root_section_name_field

    async def test_project_textfield_trigger_root_name_update(
        project_dto: ProjectDetailsDto, root_b_node, root_section_name_field
    ):
        expected_value = StringFieldValueDto(text="this is my new name")
        response = await ac.put_json(
            f"/api/projects/{project_dto.id}/container/{root_section_name_field.id}/value",
            expected_value,
        )

        root_section = await get_containers_by_type(ac, project_dto.id, root_b_node.id)
        assert root_section.label == expected_value.text

    async def _create_new_collection2(project_dto: ProjectDetailsDto, root_b_node):
        await ac.post_json(
            f"/api/projects/{project_dto.id}/container/collection",
            ProjectNodeCollectionTargetDto(
                parent_node_id=None, collection_type_id=root_b_node.id
            ),
        )

    fake_db = await db_helper.load_fixtures(SuperUser(), ProjectWithTrigger())
    await ac.login_super_user()

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

    project_dto = await create_project(ac, fake_db)
    await project_checkbox_toogle_visibility_root_collection(
        project_dto, root_b_node, checkbox_node
    )
    root_section_name_field = await create_new_collection(
        project_dto, root_b_node, textbox_node
    )
    await test_project_textfield_trigger_root_name_update(
        project_dto, root_b_node, root_section_name_field
    )
    await _create_new_collection2(project_dto, root_b_node)
