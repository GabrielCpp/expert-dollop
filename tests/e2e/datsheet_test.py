from pydantic.tools import parse_obj_as
import pytest
from collections import defaultdict
from ..fixtures import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *


def assert_all_definition_where_impemented(datasheet_definition_elements, results):
    implementations = defaultdict(int)

    for result in results:
        implementations[result.element_def_id] += 1

    assert len(datasheet_definition_elements) > 0
    for definition_element in datasheet_definition_elements:
        assert definition_element.id in implementations
        assert implementations.get(definition_element.id) == 1


async def create_datasheet(ac, definition: ProjectDefinition):
    datasheet = DatasheetDtoFactory(project_definition_id=definition.id)
    datasheet_dto = await ac.post_json(
        "/api/datasheets", datasheet, unwrap_with=DatasheetDto
    )
    return datasheet_dto


@pytest.mark.asyncio
async def test_datasheet(ac, db_helper: DbFixtureHelper):
    datasheet_element_child_json = {"lost": 3}

    async def get_paginated_datasheet_elements(datasheet_dto: DatasheetDto):
        elements_page_dto = await ac.get_json(
            f"/api/datasheets/{datasheet_dto.id}/elements",
            unwrap_with=bind_page_dto(DatasheetElementDto),
        )
        assert len(elements_page_dto.results) == 2
        return elements_page_dto

    async def update_single_instance_datasheet_element(
        datasheet_dto: DatasheetDto,
        elements_page_dto: PageDto[DatasheetElementDto],
        definition_element: DatasheetDefinitionElement,
    ):
        element = next(
            result
            for result in elements_page_dto.results
            if result.element_def_id == definition_element.id
        )

        new_child_element = await ac.put_json(
            f"/api/datasheets/{datasheet_dto.id}/element/{element.element_def_id}/{element.child_element_reference}",
            datasheet_element_child_json,
            unwrap_with=DatasheetElementDto,
        )

        datasheet_element_child = await ac.get_json(
            f"/api/datasheets/{datasheet_dto.id}/element/{element.element_def_id}/{element.child_element_reference}",
            unwrap_with=DatasheetElementDto,
        )

        assert new_child_element == datasheet_element_child

    async def instanciate_collection_element(
        datasheet_dto: DatasheetDto,
        datasheet_element_page: PageDto[DatasheetElementDto],
        definition_element: DatasheetDefinitionElement,
    ):

        element = next(
            result
            for result in datasheet_element_page.results
            if result.element_def_id == definition_element.id
        )

        new_child_element = await ac.post_json(
            f"/api/datasheets/{datasheet_dto.id}/element_collection/{element.element_def_id}",
            datasheet_element_child_json,
            unwrap_with=DatasheetElementDto,
        )

        datasheet_element_child = await ac.get_json(
            f"/api/datasheets/{datasheet_dto.id}/element/{new_child_element.element_def_id}/{new_child_element.child_element_reference}",
            unwrap_with=DatasheetElementDto,
        )
        assert new_child_element == datasheet_element_child

        return new_child_element

    async def delete_collection_element(
        datasheet_dto: DatasheetDto, new_child_element_dto: DatasheetElementDto
    ):
        await ac.delete_json(
            f"/api/datasheets/{datasheet_dto.id}/element_collection/{new_child_element_dto.element_def_id}/{new_child_element_dto.child_element_reference}",
        )

        await ac.get_json(
            f"/api/datasheets/{datasheet_dto.id}/element/{new_child_element_dto.element_def_id}/{new_child_element_dto.child_element_reference}",
            expected_status_code=404,
        )

    db = await db_helper.load_fixtures(SuperUser(), MiniDatasheet())
    await ac.login_super_user()

    definition = db.get_only_one(ProjectDefinition)
    collection_element = db.get_only_one_matching(
        DatasheetDefinitionElement, lambda e: e.name == "collection_element"
    )
    single_element = db.get_only_one_matching(
        DatasheetDefinitionElement, lambda n: n.name == "single_element"
    )
    datasheet_dto = await create_datasheet(ac, definition)
    elements_page_dto = await get_paginated_datasheet_elements(datasheet_dto)
    assert_all_definition_where_impemented(
        db.all(DatasheetDefinitionElement), elements_page_dto.results
    )

    await update_single_instance_datasheet_element(
        datasheet_dto, elements_page_dto, single_element
    )
    new_child_element_dto = await instanciate_collection_element(
        datasheet_dto, elements_page_dto, collection_element
    )
    await delete_collection_element(datasheet_dto, new_child_element_dto)


@pytest.mark.asyncio
async def test_datasheet_crud(ac, db_helper: DbFixtureHelper):
    async def clone_datasheet(datasheet_dto: DatasheetDto):
        datasheet_clone_target = DatasheetCloneTargetDto(
            target_datasheet_id=datasheet_dto.id, new_name="Renamed datasheet"
        )
        cloned_datasheet_dto = await ac.post_json(
            f"/api/datasheets/{datasheet_dto.id}/clone",
            datasheet_clone_target,
            unwrap_with=DatasheetDto,
        )
        assert cloned_datasheet_dto.name == datasheet_clone_target.new_name

        actual_datasheet_dto = await ac.get_json(
            f"/api/datasheets/{cloned_datasheet_dto.id}", unwrap_with=DatasheetDto
        )
        assert actual_datasheet_dto == cloned_datasheet_dto

        return cloned_datasheet_dto

    async def patch_datasheet(cloned_datasheet_dto: DatasheetDto):
        update_dto = DatasheetUpdateDto(
            id=cloned_datasheet_dto.id,
            updates=DatasheetUpdatableProperties(name="patched name"),
        )
        updated_datasheet_dto = await ac.patch_json(
            f"/api/datasheets/{cloned_datasheet_dto.id}",
            update_dto,
            unwrap_with=DatasheetDto,
        )
        assert updated_datasheet_dto.name == "patched name"

        actual_datasheet = await ac.get_json(
            f"/api/datasheets/{cloned_datasheet_dto.id}", unwrap_with=DatasheetDto
        )
        assert actual_datasheet == updated_datasheet_dto

    async def delete_datasheet(datasheet_dto: DatasheetDto):
        await ac.delete_json(f"/api/datasheets/{datasheet_dto.id}")
        await ac.get_json(
            f"/api/datasheets/{datasheet_dto.id}", expected_status_code=404
        )

    db = await db_helper.load_fixtures(
        SuperUser(), MiniDatasheet(), GrantRessourcePermissions()
    )
    await ac.login_super_user()

    definition = db.get_only_one(ProjectDefinition)
    datasheet_dto = await create_datasheet(ac, definition)
    cloned_datasheet_dto = await clone_datasheet(datasheet_dto)
    await patch_datasheet(cloned_datasheet_dto)
    await delete_datasheet(datasheet_dto)
