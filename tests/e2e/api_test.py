import pytest
from uuid import uuid4
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *
from expert_dollup.shared.starlette_injection import make_page_model
from expert_dollup.shared.database_services import CollectionService
from ..fixtures import *


@pytest.fixture(autouse=True)
async def wip_db(dal):
    await dal.truncate_db()


@pytest.mark.asyncio
async def test_given_project_definition_should_be_able_to_create_delete_update(ac):
    expected_project_definition = ProjectDefinitionDtoFactory()
    response = await ac.post(
        "/api/project_definition", data=expected_project_definition.json()
    )
    assert response.status_code == 200, response.text

    response = await ac.get(f"/api/project_definition/{expected_project_definition.id}")
    assert response.status_code == 200, response.text

    actual = unwrap(response, ProjectDefinitionDto)
    assert actual == expected_project_definition

    response = await ac.delete(
        f"/api/project_definition/{expected_project_definition.id}"
    )
    assert response.status_code == 200, response.text

    response = await ac.get(f"/api/project_definition/{expected_project_definition.id}")
    assert response.status_code == 404, response.text


@pytest.mark.asyncio
async def test_given_project_definition_node_should_be_able_to_create_update_delete(
    ac,
):
    project_definition = ProjectDefinitionDtoFactory()
    expected_project_definition_node = ProjectDefinitionNodeDtoFactory(
        project_definition_id=project_definition.id
    )

    response = await ac.post("/api/project_definition", data=project_definition.json())
    assert response.status_code == 200, response.json()

    response = await ac.post(
        "/api/project_definition_node",
        data=expected_project_definition_node.json(by_alias=True),
    )
    assert response.status_code == 200, response.json()

    response = await ac.get(
        f"/api/project_definition/{project_definition.id}/node/{expected_project_definition_node.id}"
    )
    assert response.status_code == 200, response.json()

    actual = unwrap(response, ProjectDefinitionNodeDto)
    assert actual == expected_project_definition_node

    response = await ac.delete(
        f"/api/project_definition/{project_definition.id}/node/{expected_project_definition_node.id}"
    )
    assert response.status_code == 200, response.json()

    response = await ac.get(
        f"/api/project_definition/{project_definition.id}/node/{expected_project_definition_node.id}"
    )
    assert response.status_code == 404, response.json()


@pytest.mark.asyncio
async def test_given_translation_should_be_able_to_create_update_delete(
    ac, static_clock
):
    project_definition = ProjectDefinitionDtoFactory()
    translation_input = TranslationInputDtoFactory(ressource_id=project_definition.id)

    response = await ac.post("/api/project_definition", data=project_definition.json())
    assert response.status_code == 200, response.json()

    response = await ac.post("/api/translation", data=translation_input.json())
    assert response.status_code == 200, response.json()

    response = await ac.get(
        f"/api/translation/{translation_input.ressource_id}/{translation_input.scope}/{translation_input.locale}/{translation_input.name}"
    )
    assert response.status_code == 200, response.json()

    expected_translation = TranslationDto(
        **translation_input.dict(), creation_date_utc=static_clock.utcnow()
    )
    actual = unwrap(response, TranslationDto)
    assert actual == expected_translation

    response = await ac.delete(
        f"/api/translation/{translation_input.ressource_id}/{translation_input.scope}/{translation_input.locale}/{translation_input.name}"
    )
    assert response.status_code == 200, response.json()

    response = await ac.get(
        f"/api/translation/{translation_input.ressource_id}/{translation_input.scope}/{translation_input.locale}/{translation_input.name}"
    )
    assert response.status_code == 404, response.json()


@pytest.mark.asyncio
async def test_given_translation_should_be_able_to_retrieve_it(
    ac, db_helper, map_dao_to_dto, static_clock
):
    ressource_id = uuid4()
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

    await db_helper.insert_daos(
        CollectionService[Translation], list(translations.values())
    )

    response = await ac.get(f"/api/translation/{ressource_id}/fr-CA")
    assert response.status_code == 200

    actual = unwrap(response, PageDto)
    assert actual == expected_translations
