import pytest
from datetime import datetime, timezone
from typing import Dict, Type, List, Callable, Any, TypeVar
from pydantic import BaseModel
from uuid import uuid4
from starlette.responses import Response
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *
from ..fixtures import *


@pytest.mark.asyncio
async def test_given_project_definition_should_be_able_to_create_delete_update(ac):
    expected_project_definition = ProjectDefinitionDtoFactory()
    response = await ac.post(
        "/api/project_definition", data=expected_project_definition.json()
    )
    assert response.status_code == 200

    response = await ac.get(f"/api/project_definition/{expected_project_definition.id}")
    assert response.status_code == 200

    actual = unwrap(response, ProjectDefinitionDto)
    assert actual == expected_project_definition

    response = await ac.delete(
        f"/api/project_definition/{expected_project_definition.id}"
    )
    assert response.status_code == 200

    response = await ac.get(f"/api/project_definition/{expected_project_definition.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_given_project_definition_node_should_be_able_to_create_update_delete(
    ac,
):
    project_definition = ProjectDefinitionDtoFactory()
    expected_project_definition_node = ProjectDefinitionNodeDtoFactory(
        project_def_id=project_definition.id
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
    ac, dal, map_dao_to_dto, static_clock
):
    ressource_id = uuid4()
    translations = dict(
        a_fr=TranslationDao(
            id=UUID("96492b2d-49fa-4250-b655-ff8cf5030953"),
            ressource_id=ressource_id,
            scope=ressource_id,
            locale="fr",
            name="a",
            value="a_fr",
            creation_date_utc=static_clock.utcnow(),
        ),
        a_en=TranslationDao(
            id=UUID("96492b2d-49fa-4250-b655-ff8cf5030954"),
            ressource_id=ressource_id,
            scope=ressource_id,
            locale="en",
            name="a",
            value="a_en",
            creation_date_utc=static_clock.utcnow(),
        ),
        b_fr=TranslationDao(
            id=UUID("96492b2d-49fa-4250-b655-ff8cf5030955"),
            ressource_id=ressource_id,
            scope=ressource_id,
            locale="fr",
            name="b",
            value="b_fr",
            creation_date_utc=static_clock.utcnow(),
        ),
    )

    dto_translations = map_dao_to_dto(
        translations, TranslationDto, Translation, TranslationDto
    )

    expected_translations = TranslationPageDto(
        next_page_token="OTY0OTJiMmQtNDlmYS00MjUwLWI2NTUtZmY4Y2Y1MDMwOTUz",
        limit=10,
        results=[dto_translations["b_fr"], dto_translations["a_fr"]],
    )

    await populate_db(dal, translation_table, translations)

    response = await ac.get(f"/api/translation/{ressource_id}/fr")
    assert response.status_code == 200

    actual = unwrap(response, TranslationPageDto)
    assert actual == expected_translations
