import pytest
from ..fixtures import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *


@pytest.mark.asyncio
async def test_datasheet_definition(ac):
    await ac.login_super_user()
    runner = FlowRunner()

    @runner.step
    async def create_datasheet_definition():
        expected_definition = ProjectDefinitionDtoFactory()
        definition = await ac.post_json(
            "/api/definitions", expected_definition, unwrap_with=ProjectDefinitionDto
        )
        assert definition.json(
            exclude={"id", "creation_date_utc"}
        ) == expected_definition.json(exclude={"id", "creation_date_utc"})

        return (definition,)

    @runner.step
    async def create_datasheet_definition_element(
        project_definition: ProjectDefinitionDto,
    ):
        datasheet_definition_element = DatasheetDefinitionElementDtoFactory(
            project_definition_id=project_definition.id
        )
        await ac.post_json(
            "/api/datasheet_definition_element", datasheet_definition_element
        )

        return (project_definition, datasheet_definition_element)

    @runner.step
    async def get_datasheet_definition(
        project_definition: ProjectDefinitionDto,
        datasheet_definition_element: DatasheetDefinitionElementDto,
    ):
        datasheet_definition_returned = await ac.get_json(
            f"/api/definitions/{project_definition.id}",
            unwrap_with=ProjectDefinitionDto,
        )
        assert project_definition == datasheet_definition_returned

        return (project_definition, datasheet_definition_element)

    @runner.step
    async def get_datasheet_definition_element(
        project_definition: ProjectDefinitionDto,
        datasheet_definition_element: DatasheetDefinitionElementDto,
    ):
        element_definition = await ac.get_json(
            f"/api/datasheet_definition_element/{datasheet_definition_element.id}",
            unwrap_with=DatasheetDefinitionElementDto,
        )
        assert datasheet_definition_element == element_definition

        return (project_definition, datasheet_definition_element)

    @runner.step
    async def delete_datasheet_definition_element(
        project_definition: ProjectDefinitionDto,
        datasheet_definition_element: DatasheetDefinitionElementDto,
    ):
        await ac.delete_json(
            f"/api/datasheet_definition_element/{datasheet_definition_element.id}"
        )

        await ac.get_json(
            f"/api/datasheet_definition_element/{datasheet_definition_element.id}",
            expected_status_code=404,
        )

        return (project_definition, datasheet_definition_element)

    @runner.step
    async def delete_datasheet_definition(
        project_definition: ProjectDefinitionDto,
        datasheet_definition_element: DatasheetDefinitionElementDto,
    ):
        await ac.delete_json(f"/api/definitions/{project_definition.id}")
        await ac.get_json(
            f"/api/definitions/{project_definition.id}", expected_status_code=404
        )

        return (project_definition, datasheet_definition_element)

    await runner.run()


@pytest.mark.asyncio
async def test_label_collection(ac, db_helper: DbFixtureHelper):
    await ac.login_super_user()
    runner = FlowRunner()
    mini_datasheet = await db_helper.load_fixtures(MiniDatasheet())

    @runner.step
    async def create_label_collection():
        label_collection = LabelCollectionDtoFactory(
            project_definition_id=mini_datasheet.get_only_one(ProjectDefinition).id
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
