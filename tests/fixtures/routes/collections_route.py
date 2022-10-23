from ..integrated_test_client import IntegratedTestClient
from expert_dollup.app.dtos import *


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
