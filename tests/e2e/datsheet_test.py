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


@pytest.mark.asyncio
async def test_datasheet(ac, db_helper: DbFixtureHelper):
    runner = FlowRunner()
    mini_datasheet = await db_helper.load_fixtures(MiniDatasheet)
    project_definition_id = mini_datasheet.get_only_one(ProjectDefinition).id

    @runner.step
    async def create_datasheet():
        datasheet = DatasheetDtoFactory(project_definition_id=project_definition_id)
        response = await ac.post("/api/datasheet", data=datasheet.json())
        assert response.status_code == 200, response.json()

        datasheet = parse_obj_as(DatasheetDto, response.json())
        return (datasheet,)

    @runner.step
    async def get_all_datasheet_elements(datasheet: DatasheetDto):
        response = await ac.get(f"/api/datasheet/{datasheet.id}/elements")
        assert response.status_code == 200, response.json()

        datasheet_element_page = unwrap(response, DatasheetElementPageDto)
        assert len(datasheet_element_page.results) == 2

        assert_all_definition_where_impemented(
            mini_datasheet.all(DatasheetDefinitionElement),
            datasheet_element_page.results,
        )

        return (datasheet, datasheet_element_page)

    @runner.step
    async def update_single_instance_datasheet_element(
        datasheet: DatasheetDto, datasheet_element_page: DatasheetElementPageDto
    ):
        definition_element = mini_datasheet.get_only_one_matching(
            DatasheetDefinitionElement, lambda n: n.name == "single_element"
        )

        element = [
            result
            for result in datasheet_element_page.results
            if result.element_def_id == definition_element.id
        ][0]

        datasheet_element_child_json = '{ "lost": 3 }'

        response = await ac.put(
            f"/api/datasheet/{datasheet.id}/element/{element.element_def_id}/{element.child_element_reference}",
            data=datasheet_element_child_json,
        )
        assert response.status_code == 200, response.json()
        new_child_element = unwrap(response, DatasheetElementDto)

        response = await ac.get(
            f"/api/datasheet/{datasheet.id}/element/{element.element_def_id}/{element.child_element_reference}",
        )
        assert response.status_code == 200, response.json()

        datasheet_element_child = unwrap(response, DatasheetElementDto)
        assert new_child_element == datasheet_element_child

        return (datasheet, datasheet_element_page)

    @runner.step
    async def instanciate_collection_element(
        datasheet: DatasheetDto, datasheet_element_page: DatasheetElementPageDto
    ):
        datasheet_element_child_json = '{ "lost": 3 }'
        definition_element = mini_datasheet.get_only_one_matching(
            DatasheetDefinitionElement, lambda e: e.name == "collection_element"
        )

        element = [
            result
            for result in datasheet_element_page.results
            if result.element_def_id == definition_element.id
        ][0]

        response = await ac.post(
            f"/api/datasheet/{datasheet.id}/element_collection/{element.element_def_id}",
            data=datasheet_element_child_json,
        )
        assert response.status_code == 200, response.json()
        new_child_element = unwrap(response, DatasheetElementDto)

        response = await ac.get(
            f"/api/datasheet/{datasheet.id}/element/{new_child_element.element_def_id}/{new_child_element.child_element_reference}",
        )
        assert response.status_code == 200, response.json()

        datasheet_element_child = unwrap(response, DatasheetElementDto)
        assert new_child_element == datasheet_element_child

        return (datasheet, new_child_element)

    @runner.step
    async def delete_collection_element(
        datasheet: DatasheetDto, new_child_element: DatasheetElementDto
    ):
        response = await ac.delete(
            f"/api/datasheet/{datasheet.id}/element_collection/{new_child_element.element_def_id}/{new_child_element.child_element_reference}",
        )
        assert response.status_code == 200, response.json()

        response = await ac.get(
            f"/api/datasheet/{datasheet.id}/element/{new_child_element.element_def_id}/{new_child_element.child_element_reference}",
        )
        assert response.status_code == 404, response.json()

    await runner.run()


@pytest.mark.asyncio
async def test_datasheet_crud(ac, db_helper: DbFixtureHelper):
    runner = FlowRunner()
    mini_datasheet = await db_helper.load_fixtures(MiniDatasheet)
    project_definition = mini_datasheet.get_only_one(ProjectDefinition)

    @runner.step
    async def create_datasheet():
        datasheet = DatasheetDtoFactory(project_definition_id=project_definition.id)
        response = await ac.post("/api/datasheet", data=datasheet.json())
        assert response.status_code == 200, response.json()

        datasheet = parse_obj_as(DatasheetDto, response.json())
        return (datasheet,)

    @runner.step
    async def clone_datasheet(datasheet: DatasheetDto):
        datasheet_clone_target = DatasheetCloneTargetDto(
            target_datasheet_id=datasheet.id, new_name="Renamed datasheet"
        )
        response = await ac.post(
            f"/api/datasheet/{datasheet.id}/clone", data=datasheet_clone_target.json()
        )
        assert response.status_code == 200, response.json()

        cloned_datasheet = unwrap(response, DatasheetDto)
        assert cloned_datasheet.name == datasheet_clone_target.new_name

        response = await ac.get(f"/api/datasheet/{cloned_datasheet.id}")
        assert response.status_code == 200, response.json()

        actual_datasheet = unwrap(response, DatasheetDto)
        assert actual_datasheet == cloned_datasheet

        return (datasheet, cloned_datasheet)

    @runner.step
    async def update_datasheet(datasheet: DatasheetDto, cloned_datasheet: DatasheetDto):
        update_dto = DatasheetUpdateDto(
            id=cloned_datasheet.id,
            updates=DatasheetUpdatableProperties(name="patched name"),
        )
        response = await ac.patch("/api/datasheet", data=update_dto.json())
        assert response.status_code == 200, response.json()

        updated_datasheet = unwrap(response, DatasheetDto)
        assert updated_datasheet.name == "patched name"

        response = await ac.get(f"/api/datasheet/{cloned_datasheet.id}")
        assert response.status_code == 200, response.json()

        actual_datasheet = unwrap(response, DatasheetDto)
        assert actual_datasheet == updated_datasheet

        return (datasheet,)

    @runner.step
    async def delete_datasheet(datasheet: DatasheetDto):
        response = await ac.delete(f"/api/datasheet/{datasheet.id}")
        assert response.status_code == 200, response.json()

        response = await ac.get(f"/api/datasheet/{datasheet.id}")
        assert response.status_code == 404, response.json()

    await runner.run()
