import pytest
from ..fixtures import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *


@pytest.mark.asyncio
async def test_datasheet_definition(ac):
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
    aggregate_dto = await create_aggregate(
        ac, definition_dto, collection_dto, NewAggregateDtoFactory()
    )

    actual_definition = await find_definition_by_id(ac, definition_dto.id)
    assert definition_dto == actual_definition

    actual_aggregate = await find_aggregate_by_id(
        ac, definition_dto.id, collection_dto.id, aggregate_dto.id
    )
    assert aggregate_dto == actual_aggregate

    await delete_aggregate_element(definition_dto, collection_dto, aggregate_dto)
    await check_aggregate_is_gone(definition_dto)


@pytest.mark.asyncio
async def test_label_collection(ac, db_helper: DbFixtureHelper):
    db = await db_helper.load_fixtures(
        SuperUser(), MiniDatasheet(), GrantRessourcePermissions()
    )
    await ac.login_super_user()

    definition = db.get_only_one(ProjectDefinition)
    collection_dto = await create_collection(
        ac, definition, NewAggregateCollectionDtoFactory()
    )
    actual_collection = await get_collection_by_id(ac, definition, collection_dto.id)
    assert actual_collection == collection_dto

    aggregate_dto = await create_aggregate(
        ac, definition, collection_dto, NewAggregateDtoFactory()
    )
    actual_aggregate_dto = await find_aggregate_by_id(
        ac, definition.id, collection_dto.id, aggregate_dto.id
    )
    assert actual_aggregate_dto == aggregate_dto

    await delete_aggregate_by_id(ac, definition.id, aggregate_dto.id)
    await ac.get_json(
        f"/api/definitions/{definition.id}/labels/{aggregate_dto.id}",
        expected_status_code=404,
    )

    await delete_collection_by_id(ac, definition.id, collection_dto.id)
    await ac.get_json(
        f"/api/definitions/{definition.id}/collections/{collection_dto.id}",
        expected_status_code=404,
    )
