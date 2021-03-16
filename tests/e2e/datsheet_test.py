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


class VarBucket:
    def __init__(self, **properties):
        self.__dict__.update(properties)

    def __setattr__(self, name, value):
        assert not name in self.__dict__, "Name in bucket cannot be overided"
        self.__dict__[name] = value
        return value


class GetIn:
    def __init__(self, *path):
        self.path = path

    def __call__(self, obj):
        result = obj

        for index in range(0, len(self.path)):
            item = self.path[index]
            result_before = result

            if isinstance(result, list):
                assert isinstance(item, tuple)
                result = self._handle_list(result, item)
            elif isinstance(result, dict):
                assert isinstance(item, str)
                result = result[item]
            else:
                assert isinstance(item, str)
                result = getattr(result, item)

            if result_before is result:
                raise Exception("Value not found")

        return result

    def _handle_list(self, obj, item):
        (property_name, expected_value) = item
        result = None

        for element in obj:
            if isinstance(element, list):
                result = self._handle_list(element, item)
            elif (
                isinstance(element, dict) and element[property_name] == expected_value
            ) or (getattr(element, property_name) == expected_value):
                result = element

            if not result is None:
                break

        return result


@pytest.mark.asyncio
async def test_datasheet(ac, mini_datasheet: MiniDatasheet):
    runner = FlowRunner()
    ctx = VarBucket()

    @runner.step
    async def create_datasheet():
        ctx.datasheet_definition = mini_datasheet.datasheet_definitions[0]
        ctx.datasheet = DatasheetDtoFactory(
            datasheet_def_id=ctx.datasheet_definition.id
        )
        response = await ac.post("/api/datasheet", data=ctx.datasheet.json())
        assert response.status_code == 200, response.json()

    @runner.step
    async def get_all_datasheet_elements():
        response = await ac.get(f"/api/datasheet/{ctx.datasheet.id}/elements")
        assert response.status_code == 200, response.json()

        ctx.datasheet_element_page = unwrap(response, DatasheetElementPageDto)
        assert len(ctx.datasheet_element_page.results) == 2

        assert_all_definition_where_impemented(
            mini_datasheet.datasheet_definition_elements,
            ctx.datasheet_element_page.results,
        )

    @runner.step
    async def update_single_instance_datasheet_element():
        definition_element = GetIn(
            "datasheet_definition_elements", ("name", "single_element")
        )(mini_datasheet)

        element = GetIn(("element_def_id", definition_element.id))(
            ctx.datasheet_element_page.results
        )

        datasheet_element_child_json = '{ "lost": 3 }'

        response = await ac.put(
            f"/api/datasheet/{ctx.datasheet.id}/element/{element.element_def_id}/{element.child_element_reference}",
            data=datasheet_element_child_json,
        )
        assert response.status_code == 200, response.json()
        new_child_element = unwrap(response, DatasheetElementDto)

        response = await ac.get(
            f"/api/datasheet/{ctx.datasheet.id}/element/{element.element_def_id}/{element.child_element_reference}",
        )
        assert response.status_code == 200, response.json()

        datasheet_element_child = unwrap(response, DatasheetElementDto)
        assert new_child_element == datasheet_element_child

    @runner.step
    async def instanciate_collection_element():
        datasheet_element_child_json = '{ "lost": 3 }'
        definition_element = GetIn(
            "datasheet_definition_elements", ("name", "collection_element")
        )(mini_datasheet)

        element = GetIn(("element_def_id", definition_element.id))(
            ctx.datasheet_element_page.results
        )

        response = await ac.post(
            f"/api/datasheet/{ctx.datasheet.id}/element_collection/{element.element_def_id}",
            data=datasheet_element_child_json,
        )
        assert response.status_code == 200, response.json()
        new_child_element = unwrap(response, DatasheetElementDto)

        response = await ac.get(
            f"/api/datasheet/{ctx.datasheet.id}/element/{new_child_element.element_def_id}/{new_child_element.child_element_reference}",
        )
        assert response.status_code == 200, response.json()

        datasheet_element_child = unwrap(response, DatasheetElementDto)
        assert new_child_element == datasheet_element_child

        return (new_child_element,)

    @runner.step
    async def delete_collection_element(new_child_element):
        response = await ac.delete(
            f"/api/datasheet/{ctx.datasheet.id}/element_collection/{new_child_element.element_def_id}/{new_child_element.child_element_reference}",
        )
        assert response.status_code == 200, response.json()

        response = await ac.get(
            f"/api/datasheet/{ctx.datasheet.id}/element/{new_child_element.element_def_id}/{new_child_element.child_element_reference}",
        )
        assert response.status_code == 404, response.json()

    await runner.run()


@pytest.mark.asyncio
async def test_datasheet_crud(ac, mini_datasheet: MiniDatasheet):
    runner = FlowRunner()
    ctx = VarBucket()

    @runner.step
    async def create_datasheet():
        ctx.datasheet_definition = mini_datasheet.datasheet_definitions[0]
        ctx.datasheet = DatasheetDtoFactory(
            datasheet_def_id=ctx.datasheet_definition.id
        )
        response = await ac.post("/api/datasheet", data=ctx.datasheet.json())
        assert response.status_code == 200, response.json()

    @runner.step
    async def clone_datsheet():
        datasheet_clone_target = DatasheetCloneTargetDto(
            target_datasheet_id=ctx.datasheet.id, new_name="Renamed datasheet"
        )
        response = await ac.post(
            f"/api/datasheet/clone", data=datasheet_clone_target.json()
        )
        assert response.status_code == 200, response.json()

        cloned_datasheet = unwrap(response, DatasheetDto)
        assert cloned_datasheet.name == datasheet_clone_target.new_name

        response = await ac.get(f"/api/datasheet/{cloned_datasheet.id}")
        assert response.status_code == 200, response.json()

        actual_datasheet = unwrap(response, DatasheetDto)
        assert actual_datasheet == cloned_datasheet

        return (cloned_datasheet,)

    @runner.step
    async def update_datasheet(cloned_datasheet: DatasheetDto):
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

    @runner.step
    async def delete_datasheet():
        response = await ac.delete(f"/api/datasheet/{ctx.datasheet.id}")
        assert response.status_code == 200, response.json()

        response = await ac.get(f"/api/datasheet/{ctx.datasheet.id}")
        assert response.status_code == 404, response.json()

    await runner.run()
