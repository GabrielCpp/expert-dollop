import pytest
from uuid import uuid4
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *
from expert_dollup.shared.starlette_injection import make_page_model
from expert_dollup.shared.database_services import InternalRepository
from ..fixtures import *


@pytest.mark.asyncio
async def test_given_project_definition_should_be_able_to_create_delete_update(ac):
    await ac.login_super_user()

    expected_project_definition = ProjectDefinitionDtoFactory()
    await ac.post_json("/api/definitions", expected_project_definition)

    actual = await ac.get_json(
        f"/api/definitions/{expected_project_definition.id}",
        unwrap_with=ProjectDefinitionDto,
    )
    assert actual == expected_project_definition

    await ac.delete_json(f"/api/definitions/{expected_project_definition.id}")

    await ac.get_json(
        f"/api/definitions/{expected_project_definition.id}", expected_status_code=404
    )


@pytest.mark.asyncio
async def test_given_project_definition_node_should_be_able_to_create_update_delete(
    ac,
):
    await ac.login_super_user()
    definition = ProjectDefinitionDtoFactory()
    expected_definition_node = ProjectDefinitionNodeDtoFactory(
        project_definition_id=definition.id
    )

    await ac.post_json("/api/definitions", definition)

    created_node = await ac.post_json(
        f"/api/definitions/{definition.id}/nodes",
        expected_definition_node,
        unwrap_with=ProjectDefinitionNodeDto,
    )
    assert created_node.dict(
        exclude={"id", "creation_date_utc"}
    ) == expected_definition_node.dict(exclude={"id", "creation_date_utc"})

    actual = await ac.get_json(
        f"/api/definitions/{definition.id}/nodes/{created_node.id}",
        unwrap_with=ProjectDefinitionNodeDto,
    )
    assert actual == created_node

    await ac.delete_json(f"/api/definitions/{definition.id}/nodes/{created_node.id}")

    await ac.get_json(
        f"/api/definitions/{definition.id}/nodes/{created_node.id}",
        expected_status_code=404,
    )


@pytest.mark.asyncio
async def test_given_translation_should_be_able_to_create_update_delete(
    ac, static_clock
):
    await ac.login_super_user()
    project_definition = ProjectDefinitionDtoFactory()
    translation_input = TranslationInputDtoFactory(ressource_id=project_definition.id)

    await ac.post_json("/api/definitions", project_definition)
    await ac.post_json("/api/translations", translation_input)

    expected_translation = TranslationDto(
        **translation_input.dict(), creation_date_utc=static_clock.utcnow()
    )
    actual = await ac.get_json(
        f"/api/translations/{translation_input.ressource_id}/{translation_input.scope}/{translation_input.locale}/{translation_input.name}",
        unwrap_with=TranslationDto,
    )
    assert actual == expected_translation

    await ac.delete_json(
        f"/api/translations/{translation_input.ressource_id}/{translation_input.scope}/{translation_input.locale}/{translation_input.name}"
    )

    await ac.get_json(
        f"/api/translations/{translation_input.ressource_id}/{translation_input.scope}/{translation_input.locale}/{translation_input.name}",
        expected_status_code=404,
    )


@pytest.mark.asyncio
async def test_given_translation_should_be_able_to_retrieve_it(
    ac, container, map_dao_to_dto, static_clock
):
    await ac.login_super_user()
    definition = await ac.post_json(
        "/api/definitions",
        ProjectDefinitionDtoFactory(),
        unwrap_with=ProjectDefinitionDto,
    )
    ressource_id = definition.id

    translations = dict(
        a_fr=TranslationDao(
            id=UUID("96492b2d-49fa-4250-b655-ff8cf5030953"),
            ressource_id=ressource_id,
            scope=ressource_id,
            locale="fr-CA",
            name="a",
            value="a_fr",
            creation_date_utc=static_clock.utcnow(),
        ),
        a_en=TranslationDao(
            id=UUID("96492b2d-49fa-4250-b655-ff8cf5030954"),
            ressource_id=ressource_id,
            scope=ressource_id,
            locale="en-US",
            name="a",
            value="a_en",
            creation_date_utc=static_clock.utcnow(),
        ),
        b_fr=TranslationDao(
            id=UUID("96492b2d-49fa-4250-b655-ff8cf5030955"),
            ressource_id=ressource_id,
            scope=ressource_id,
            locale="fr-CA",
            name="b",
            value="b_fr",
            creation_date_utc=static_clock.utcnow(),
        ),
    )

    dto_translations = map_dao_to_dto(
        translations, TranslationDto, Translation, TranslationDto
    )

    PageDto = make_page_model(TranslationDto)

    expected_translations = PageDto(
        next_page_token="OTY0OTJiMmQtNDlmYS00MjUwLWI2NTUtZmY4Y2Y1MDMwOTUz",
        has_next_page=True,
        limit=10,
        results=[dto_translations["b_fr"], dto_translations["a_fr"]],
    )

    await container.get(InternalRepository[Translation]).bulk_insert(
        list(translations.values())
    )

    actual = await ac.get_json(
        f"/api/translations/{ressource_id}/fr-CA", unwrap_with=PageDto
    )
    assert actual == expected_translations
