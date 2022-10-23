import pytest
from ..fixtures import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *


@pytest.mark.asyncio
async def test_datasheet_definition(ac):
    async def create_aggregate_dto(
        definition_dto: ProjectDefinitionDto, collection_dto: AggregateCollectionDto
    ):
        aggregate_dto = await ac.post_json(
            f"/api/definitions/{definition_dto.id}/collections/{collection_dto.id}/aggregates",
            NewAggregateDtoFactory(),
            unwrap_with=AggregateDto,
        )

        return aggregate_dto

    async def get_datasheet_definition(definition_dto: ProjectDefinitionDto):
        datasheet_definition_returned = await ac.get_json(
            f"/api/definitions/{definition_dto.id}",
            unwrap_with=ProjectDefinitionDto,
        )
        assert definition_dto == datasheet_definition_returned

    async def get_datasheet_definition_element(
        definition_dto: ProjectDefinitionDto,
        collection_dto: AggregateCollection,
        aggregate_dto: AggregateDto,
    ):
        element_definition = await ac.get_json(
            f"/api/definitions/{definition_dto.id}/collections/{collection_dto.id}/aggregates/{aggregate_dto.id}",
            unwrap_with=AggregateDto,
        )
        assert definition_element_dto == element_definition

    async def delete_aggregate_element(
        definition_dto: ProjectDefinitionDto,
        collection_dto: AggregateCollection,
        aggregate_dto: AggregateDto,
    ):
        await ac.delete_json(
            f"/api/definitions/{definition_dto.id}/collections/{collection_dto.id}/aggregates/{aggregate_dto.id}"
        )

        await ac.get_json(
            f"/api/definitions/{definition_dto.id}/collections/{collection_dto.id}/aggregates/{aggregate_dto.id}",
            expected_status_code=404,
        )

    async def check_aggregate_is_gone(definition_dto: ProjectDefinitionDto):
        await ac.delete_json(f"/api/definitions/{definition_dto.id}")
        await ac.get_json(
            f"/api/definitions/{definition_dto.id}", expected_status_code=404
        )

    await ac.login_super_user()

    definition_dto = await create_definition(ac, NewDefinitionDtoFactory())
    collection_dto = await create_collection(
        ac, definition_dto, NewAggregateCollectionDtoFactory(is_abstract=True)
    )
    aggregate_dto = await create_aggregate_dto(definition_dto, collection_dto)
    await get_datasheet_definition(definition_dto)
    await get_datasheet_definition_element(definition_dto, aggregate_dto)
    await delete_aggregate_element(definition_dto, aggregate_dto)
    await check_aggregate_is_gone(definition_dto)


@pytest.mark.asyncio
async def test_label_collection(ac, db_helper: DbFixtureHelper):
    async def create_label_collection(definition: ProjectDefinition):
        collection_dto = await ac.post_json(
            f"/api/definitions/{definition.id}/label_collections",
            NewAggregateCollectionDtoFactory(project_definition_id=definition.id),
            unwrap_with=AggregateCollectionDto,
        )

        return collection_dto

    async def create_label(
        definition: ProjectDefinition,
        collection_dto: AggregateCollectionDto,
    ):
        label_dto = await ac.post_json(
            f"/api/definitions/{definition.id}/labels",
            [NewAggregateDtoFactory(label_collection_id=collection_dto.id)],
            unwrap_with=AggregateDto,
        )
        return label_dto

    async def check_label_collection_is_identical(
        collection_dto: AggregateCollectionDto,
    ):
        actual_label_collection = await ac.get_json(
            f"/api/definitions/{definition.id}/label_collections/{collection_dto.id}",
            unwrap_with=AggregateCollectionDto,
        )
        assert actual_label_collection == label_collection_dto

    async def check_label_is_the_same(
        definition: ProjectDefinition, label_dto: AggregateDto
    ):
        actual_label = await ac.get_json(
            f"/api/definitions/{definition.id}/labels/{label_dto.id}",
            unwrap_with=AggregateDto,
        )
        assert actual_label == label_dto

    async def delete_label_and_check_it_is_gone(
        definition: ProjectDefinition, label_dto: AggregateDto
    ):
        await ac.delete_json(f"/api/definitions/{definition.id}/labels/{label_dto.id}")
        await ac.get_json(
            f"/api/definitions/{definition.id}/labels/{label_dto.id}",
            expected_status_code=404,
        )

    async def delete_label_collection_and_check_it_is_gone(
        definition: ProjectDefinition,
        collection_dto: AggregateCollectionDto,
    ):
        await ac.delete_json(
            f"/api/definitions/{definition.id}/label_collections/{collection_dto.id}"
        )
        await ac.get_json(
            f"/api/definitions/{definition.id}/label_collections/{collection_dto.id}",
            expected_status_code=404,
        )

    db = await db_helper.load_fixtures(
        SuperUser(), MiniDatasheet(), GrantRessourcePermissions()
    )
    await ac.login_super_user()

    definition = db.get_only_one(ProjectDefinition)
    collection_dto = await create_label_collection(definition)
    await check_label_collection_is_identical(collection_dto)
    label_dto = await create_label(definition, collection_dto)
    await check_label_is_the_same(definition, label_dto)
    await delete_label_and_check_it_is_gone(definition, label_dto)
    await delete_label_collection_and_check_it_is_gone(definition, collection_dto)
