from uuid import UUID
from expert_dollup.app.dtos import *
from ..integrated_test_client import IntegratedTestClient


async def find_definition_by_id(
    ac: IntegratedTestClient, definition_id: UUID
) -> ProjectDefinitionDto:
    result_dto = await ac.get_json(
        f"/api/definitions/{definition_id}",
        unwrap_with=ProjectDefinitionDto,
    )
    return result_dto


async def create_definition(
    ac: IntegratedTestClient, data: NewDefinitionDto
) -> ProjectDefinitionDto:
    result_dto = await ac.post_json(
        "/api/definitions", data, unwrap_with=ProjectDefinitionDto
    )
    assert result_dto.name == data.name
    return result_dto
