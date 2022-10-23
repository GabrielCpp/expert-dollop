from ..integrated_test_client import IntegratedTestClient
from expert_dollup.app.dtos import *


async def create_definition(ac: IntegratedTestClient, data: NewDefinitionDto):
    result_dto = await ac.post_json(
        "/api/definitions", data, unwrap_with=ProjectDefinitionDto
    )
    assert result_dto.name == data.name
    return result_dto
