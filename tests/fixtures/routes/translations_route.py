from uuid import UUID
from expert_dollup.app.dtos import *
from ..integrated_test_client import IntegratedTestClient


async def create_translation(
    ac: IntegratedTestClient, definition_id: UUID, data: NewTranslationDto
) -> ProjectDefinitionDto:
    result_dto = await ac.post_json(
        f"/api/definitions/{definition_id}/translations",
        data,
        unwrap_with=TranslationDto,
    )
    assert result_dto.name == data.name
    return result_dto


async def find_translation_by_id(
    ac: IntegratedTestClient, definition_id: UUID, locale: str, name: str
):
    result_dto = await ac.get_json(
        f"/api/definitions/{definition_id}/translations/{locale}/{name}",
        unwrap_with=TranslationDto,
    )
    return result_dto


async def delete_translation_by_id(
    ac: IntegratedTestClient, definition_id: UUID, locale: str, name: str
):
    await ac.delete_json(
        f"/api/definitions/{definition_id}/translations/{locale}/{name}"
    )
    await ac.get_json(
        f"/api/definitions/{definition_id}/translations/{locale}/{name}",
        expected_status_code=404,
    )
