import pytest
from ..fixtures import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *


@pytest.mark.asyncio
async def test_datasheet_definition(ac):
    async def create_datasheet_definition():
        new_definition = NewDefinitionDtoFactory()
        definition_dto = await ac.post_json(
            "/api/definitions", new_definition, unwrap_with=ProjectDefinitionDto
        )
        assert definition_dto.name == new_definition.name
        return definition_dto

    async def create_datasheet_definition_element(
        definition_dto: ProjectDefinitionDto,
    ):
        definition_element_dto = await ac.post_json(
            f"/api/definitions/{definition_dto.id}/datasheet_elements",
            DatasheetDefinitionElementDtoFactory(
                project_definition_id=definition_dto.id
            ),
            unwrap_with=DatasheetDefinitionElementDto,
        )

        return definition_element_dto

    async def get_datasheet_definition(
        definition_dto: ProjectDefinitionDto,
        definition_element_dto: DatasheetDefinitionElementDto,
    ):
        datasheet_definition_returned = await ac.get_json(
            f"/api/definitions/{definition_dto.id}",
            unwrap_with=ProjectDefinitionDto,
        )
        assert definition_dto == datasheet_definition_returned

    async def get_datasheet_definition_element(
        definition_dto: ProjectDefinitionDto,
        definition_element_dto: DatasheetDefinitionElementDto,
    ):
        element_definition = await ac.get_json(
            f"/api/definitions/{definition_dto.id}/datasheet_elements/{definition_element_dto.id}",
            unwrap_with=DatasheetDefinitionElementDto,
        )
        assert definition_element_dto == element_definition

    async def delete_datasheet_definition_element(
        definition_dto: ProjectDefinitionDto,
        definition_element_dto: DatasheetDefinitionElementDto,
    ):
        await ac.delete_json(
            f"/api/definitions/{definition_dto.id}/datasheet_elements/{definition_element_dto.id}"
        )

        await ac.get_json(
            f"/api/definitions/{definition_dto.id}/datasheet_elements/{definition_element_dto.id}",
            expected_status_code=404,
        )

    async def check_datasheet_definition_is_gone(
        definition_dto: ProjectDefinitionDto,
        definition_element_dto: DatasheetDefinitionElementDto,
    ):
        await ac.delete_json(f"/api/definitions/{definition_dto.id}")
        await ac.get_json(
            f"/api/definitions/{definition_dto.id}", expected_status_code=404
        )

    await ac.login_super_user()

    definition_dto = await create_datasheet_definition()
    definition_element_dto = await create_datasheet_definition_element(definition_dto)
    await get_datasheet_definition(definition_dto, definition_element_dto)
    await get_datasheet_definition_element(definition_dto, definition_element_dto)
    await delete_datasheet_definition_element(definition_dto, definition_element_dto)
    await check_datasheet_definition_is_gone(definition_dto, definition_element_dto)


@pytest.mark.asyncio
async def test_label_collection(ac, db_helper: DbFixtureHelper):
    async def create_label_collection(definition: ProjectDefinition):
        label_collection = LabelCollectionDtoFactory(
            project_definition_id=definition.id
        )
        label_collection_dto = await ac.post_json(
            f"/api/definitions/{definition.id}/label_collections",
            label_collection,
            unwrap_with=LabelCollectionDto,
        )

        return label_collection_dto

    async def create_label(
        definition: ProjectDefinition,
        label_collection_dto: LabelCollectionDto,
    ):
        label = LabelDtoFactory(label_collection_id=label_collection_dto.id)
        label_dto = await ac.post_json(
            f"/api/definitions/{definition.id}/labels", label, unwrap_with=LabelDto
        )
        return label_dto

    async def check_label_collection_is_identical(
        label_collection_dto: LabelCollectionDto,
    ):
        actual_label_collection = await ac.get_json(
            f"/api/definitions/{definition.id}/label_collections/{label_collection_dto.id}",
            unwrap_with=LabelCollectionDto,
        )
        assert actual_label_collection == label_collection_dto

    async def check_label_is_the_same(
        definition: ProjectDefinition, label_dto: LabelDto
    ):
        actual_label = await ac.get_json(
            f"/api/definitions/{definition.id}/labels/{label_dto.id}",
            unwrap_with=LabelDto,
        )
        assert actual_label == label_dto

    async def delete_label_and_check_it_is_gone(
        definition: ProjectDefinition, label_dto: LabelDto
    ):
        await ac.delete_json(f"/api/definitions/{definition.id}/labels/{label_dto.id}")
        await ac.get_json(
            f"/api/definitions/{definition.id}/labels/{label_dto.id}",
            expected_status_code=404,
        )

    async def delete_label_collection_and_check_it_is_gone(
        definition: ProjectDefinition,
        label_collection_dto: LabelCollectionDto,
    ):
        await ac.delete_json(
            f"/api/definitions/{definition.id}/label_collections/{label_collection_dto.id}"
        )
        await ac.get_json(
            f"/api/definitions/{definition.id}/label_collections/{label_collection_dto.id}",
            expected_status_code=404,
        )

    db = await db_helper.load_fixtures(
        SuperUser(), MiniDatasheet(), GrantRessourcePermissions()
    )
    await ac.login_super_user()

    definition = db.get_only_one(ProjectDefinition)
    label_collection_dto = await create_label_collection(definition)
    await check_label_collection_is_identical(label_collection_dto)
    label_dto = await create_label(definition, label_collection_dto)
    await check_label_is_the_same(definition, label_dto)
    await delete_label_and_check_it_is_gone(definition, label_dto)
    await delete_label_collection_and_check_it_is_gone(definition, label_collection_dto)
