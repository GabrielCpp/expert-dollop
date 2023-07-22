from uuid import UUID
from ..integrated_test_client import IntegratedTestClient
from expert_dollup.app.dtos import *


async def get_collection_by_id(
    ac: IntegratedTestClient,
    definition_dto: ProjectDefinitionDto,
    collection_id: UUID,
):
    collection = await ac.get_json(
        f"/api/definitions/{definition_dto.id}/collections/{collection_id}",
        unwrap_with=AggregateCollectionDto,
    )
    return collection


async def create_collection(
    ac: IntegratedTestClient,
    definition_dto: ProjectDefinitionDto,
    data: NewAggregateCollectionDto,
):
    result_dto = await ac.post_json(
        f"/api/definitions/{definition_dto.id}/collections",
        data,
        unwrap_with=AggregateCollectionDto,
    )

    return result_dto


async def delete_collection_by_id(
    ac: IntegratedTestClient, definition_id: UUID, collection_id: UUID
):
    await ac.delete_json(
        f"/api/definitions/{definition_id}/collections/{collection_id}"
    )
