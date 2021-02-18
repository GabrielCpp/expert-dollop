import pytest
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
async def test_given_project_definition_container_should_be_able_to_create_update_delete(
    ac,
):
    project_definition = ProjectDefinitionDtoFactory()
    expected_project_definition_container = ProjectDefinitionContainerDtoFactory(
        project_def_id=project_definition.id
    )

    response = await ac.post("/api/project_definition", data=project_definition.json())
    assert response.status_code == 200

    response = await ac.post(
        "/api/project_definition_container",
        data=expected_project_definition_container.json(),
    )
    assert response.status_code == 200

    response = await ac.get(
        f"/api/project_definition_container/{expected_project_definition_container.id}"
    )
    assert response.status_code == 200

    actual = unwrap(response, ProjectDefinitionContainerDto)
    assert actual == expected_project_definition_container

    response = await ac.delete(
        f"/api/project_definition_container/{expected_project_definition_container.id}"
    )
    assert response.status_code == 200

    response = await ac.get(
        f"/api/project_definition_container/{expected_project_definition_container.id}"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_given_translation_should_be_able_to_create_update_delete(ac):
    project_definition = ProjectDefinitionDtoFactory()
    translation = TranslationDtoFactory(ressource_id=project_definition.id)

    response = await ac.post("/api/project_definition", data=project_definition.json())
    assert response.status_code == 200

    response = await ac.post("/api/translation", data=translation.json())
    assert response.status_code == 200

    response = await ac.get(
        f"/api/translation/{translation.ressource_id}/{translation.locale}/{translation.name}"
    )
    assert response.status_code == 200

    actual = unwrap(response, TranslationDto)
    assert actual == translation

    response = await ac.delete(
        f"/api/translation/{translation.ressource_id}/{translation.locale}/{translation.name}"
    )
    assert response.status_code == 200

    response = await ac.get(
        f"/api/translation/{translation.ressource_id}/{translation.locale}/{translation.name}"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_given_translation_should_be_able_to_retrieve_it(ac, dal, map_dao_to_dto):
    ressource_id = uuid4()
    translations = dict(
        a_fr=TranslationDao(
            ressource_id=ressource_id, locale="fr", name="a", value="a_fr"
        ),
        a_en=TranslationDao(
            ressource_id=ressource_id, locale="en", name="a", value="a_en"
        ),
        b_fr=TranslationDao(
            ressource_id=ressource_id, locale="fr", name="b", value="b_fr"
        ),
    )

    dto_translations = map_dao_to_dto(
        translations, TranslationDto, Translation, TranslationDto
    )

    expected_translations = TranslationPageDto(
        next_page_token="1",
        limit=10,
        results=[dto_translations["a_fr"], dto_translations["b_fr"]],
    )

    await populate_db(dal, translation_table, translations)

    response = await ac.get(f"/api/translation/{ressource_id}/fr")
    assert response.status_code == 200

    actual = unwrap(response, TranslationPageDto)
    assert actual == expected_translations