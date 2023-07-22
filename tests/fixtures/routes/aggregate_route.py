from uuid import UUID
from expert_dollup.app.dtos import *
from ..integrated_test_client import IntegratedTestClient


async def create_aggregate(
    ac: IntegratedTestClient,
    definition_dto: ProjectDefinitionDto,
    collection_dto: AggregateCollectionDto,
    data: NewAggregateDto,
):
    result_dto = await ac.post_json(
        f"/api/definitions/{definition_dto.id}/collections/{collection_dto.id}/aggregates",
        data,
        unwrap_with=AggregateDto,
    )
    return result_dto


async def find_aggregate_by_id(
    ac: IntegratedTestClient,
    definition_id: UUID,
    collection_id: UUID,
    aggregate_id: UUID,
) -> AggregateDto:
    result_dto = await ac.get_json(
        f"/api/definitions/{definition_id}/collections/{collection_id}/aggregates/{aggregate_id}",
        unwrap_with=AggregateDto,
    )
    return result_dto


async def delete_aggregate_by_id(
    ac: IntegratedTestClient, definition_id: UUID, aggregate_id: UUID
):
    return await ac.delete_json(
        f"/api/definitions/{definition_id}/collections/{aggregate_id}"
    )
