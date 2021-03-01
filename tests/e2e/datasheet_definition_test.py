import pytest
from ..fixtures import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *


@pytest.mark.asyncio
async def test_datasheet_definition(ac):
    runner = FlowRunner()

    @runner.step
    async def create_datasheet_definition():
        datasheet_definition = DatasheetDefinitionDtoFactory()
        response = await ac.post(
            "/api/datasheet_definition", data=datasheet_definition.json()
        )
        assert response.status_code == 200, response.json()

        return (datasheet_definition,)

    @runner.step
    async def create_datasheet_definition_element(
        datasheet_definition: DatasheetDefinitionDto,
    ):
        datasheet_definition_element = DatasheetDefinitionElementDtoFactory(
            datasheet_def_id=datasheet_definition.id
        )
        response = await ac.post(
            "/api/datasheet_definition_element",
            data=datasheet_definition_element.json(),
        )
        assert response.status_code == 200, response.json()

        return (datasheet_definition, datasheet_definition_element)

    @runner.step
    async def get_datasheet_definition(
        datasheet_definition: DatasheetDefinitionDto,
        datasheet_definition_element: DatasheetDefinitionElementDto,
    ):
        response = await ac.get(f"/api/datasheet_definition/{datasheet_definition.id}")
        assert response.status_code == 200, response.json()

        datasheet_definition_returned = unwrap(response, DatasheetDefinitionDto)
        assert datasheet_definition == datasheet_definition_returned

        return (datasheet_definition, datasheet_definition_element)

    @runner.step
    async def get_datasheet_definition_element(
        datasheet_definition: DatasheetDefinitionDto,
        datasheet_definition_element: DatasheetDefinitionElementDto,
    ):
        response = await ac.get(
            f"/api/datasheet_definition_element/{datasheet_definition_element.id}"
        )
        assert response.status_code == 200, response.json()

        element_definition = unwrap(response, DatasheetDefinitionElementDto)
        assert datasheet_definition_element == element_definition

        return (datasheet_definition, datasheet_definition_element)

    @runner.step
    async def delete_datasheet_definition_element(
        datasheet_definition: DatasheetDefinitionDto,
        datasheet_definition_element: DatasheetDefinitionElementDto,
    ):
        response = await ac.delete(
            f"/api/datasheet_definition_element/{datasheet_definition_element.id}"
        )
        assert response.status_code == 200, response.json()

        response = await ac.get(
            f"/api/datasheet_definition_element/{datasheet_definition_element.id}"
        )
        assert response.status_code == 404, response.json()

        return (datasheet_definition, datasheet_definition_element)

    @runner.step
    async def delete_datasheet_definition(
        datasheet_definition: DatasheetDefinitionDto,
        datasheet_definition_element: DatasheetDefinitionElementDto,
    ):
        response = await ac.delete(
            f"/api/datasheet_definition/{datasheet_definition.id}"
        )
        assert response.status_code == 200, response.json()

        response = await ac.get(f"/api/datasheet_definition/{datasheet_definition.id}")
        assert response.status_code == 404, response.json()

        return (datasheet_definition, datasheet_definition_element)

    await runner.run()


@pytest.mark.asyncio
async def test_label_collection(ac, mini_datasheet):
    runner = FlowRunner()

    @runner.step
    async def create_label_collection():
        label_collection = LabelCollectionDtoFactory(
            datasheet_definition_id=mini_datasheet.datasheet_definitions[0].id
        )
        response = await ac.post("/api/label_collection", data=label_collection.json())
        assert response.status_code == 200, response.json()

        return (label_collection,)

    @runner.step
    async def create_label(
        label_collection: LabelCollectionDto,
    ):
        label = LabelDtoFactory(label_collection_id=label_collection.id)
        response = await ac.post(
            "/api/label",
            data=label.json(),
        )
        assert response.status_code == 200, response.json()

        return (label_collection, label)

    @runner.step
    async def get_label_collection(
        label_collection: LabelCollectionDto,
        label: LabelDto,
    ):
        response = await ac.get(f"/api/label_collection/{label_collection.id}")
        assert response.status_code == 200, response.json()

        label_collection_returned = unwrap(response, LabelCollectionDto)
        assert label_collection == label_collection_returned

        return (label_collection, label)

    @runner.step
    async def get_label(
        label_collection: LabelCollectionDto,
        label: LabelDto,
    ):
        response = await ac.get(f"/api/label/{label.id}")
        assert response.status_code == 200, response.json()

        element_definition = unwrap(response, LabelDto)
        assert label == element_definition

        return (label_collection, label)

    @runner.step
    async def delete_label(
        label_collection: LabelCollectionDto,
        label: LabelDto,
    ):
        response = await ac.delete(f"/api/label/{label.id}")
        assert response.status_code == 200, response.json()

        response = await ac.get(f"/api/label/{label.id}")
        assert response.status_code == 404, response.json()

        return (label_collection, label)

    @runner.step
    async def delete_label_collection(
        label_collection: LabelCollectionDto,
        label: LabelDto,
    ):
        response = await ac.delete(f"/api/label_collection/{label_collection.id}")
        assert response.status_code == 200, response.json()

        response = await ac.get(f"/api/label_collection/{label_collection.id}")
        assert response.status_code == 404, response.json()

        return (label_collection, label)

    await runner.run()
