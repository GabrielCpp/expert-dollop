import pytest
import factory
from typing import Dict, Type, List, Callable, Any, TypeVar
from pydantic import BaseModel
from uuid import uuid4
from starlette.responses import Response
from expert_dollup.app.dtos import ProjectDefinitionDto, ProjectDefinitionContainerDto, TranslationDto, TranslationIdDto
from expert_dollup.infra.expert_dollup_db import translation_table, TranslationDao

Dao = TypeVar('Dao')


class ProjectDefinitionDtoFactory(factory.Factory):
    class Meta:
        model = ProjectDefinitionDto

    id = factory.LazyFunction(uuid4)
    name = factory.Sequence(lambda n: f"Gab{n}")
    default_datasheet_id = factory.LazyFunction(uuid4)
    plugins = []


class ProjectDefinitionContainerDtoFactory(factory.Factory):
    class Meta:
        model = ProjectDefinitionContainerDto

    id = factory.LazyFunction(uuid4)
    project_def_id = factory.LazyFunction(uuid4)
    name = factory.Sequence(lambda n: f"Container{n}")
    is_collection = False
    instanciate_by_default = True
    order_index = factory.Sequence(lambda n: n)
    custom_attributes = {}
    value_type = 'INT'
    default_value = {'value': 0}
    path = []


class TranslationDtoFactory(factory.Factory):
    class Meta:
        model = TranslationDto

    ressource_id = factory.LazyFunction(uuid4)
    locale = 'fr'
    name = factory.Sequence(lambda n: f"hello{n}")
    value = factory.Sequence(lambda n: f"translation{n}")


async def populate_db(db, table, daos: Dict[str, BaseModel]):
    await db.execute_many(table.insert(), [
        dao.dict() for dao in daos.values()
    ])


def unwrap(response: Response, dao: Type):
    return dao(**response.json())


def unwrap_many(response: Response, dao: Type, sort_by_key: Callable[[Dao], Any]) -> List[Dao]:
    return sorted([dao(**item) for item in response.json()], key=sort_by_key)


@pytest.mark.asyncio
async def test_given_project_definition_should_be_able_to_create_delete_update(ac):
    expected_project_definition = ProjectDefinitionDtoFactory()
    response = await ac.post("/api/project_definition", data=expected_project_definition.json())
    assert response.status_code == 200

    response = await ac.get(f"/api/project_definition/{expected_project_definition.id}")
    assert response.status_code == 200

    actual = unwrap(response, ProjectDefinitionDto)
    assert actual == expected_project_definition

    response = await ac.delete(f"/api/project_definition/{expected_project_definition.id}")
    assert response.status_code == 200

    response = await ac.get(f"/api/project_definition/{expected_project_definition.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_given_project_definition_container_should_be_able_to_create_update_delete(ac):
    project_definition = ProjectDefinitionDtoFactory()
    expected_project_definition_container = ProjectDefinitionContainerDtoFactory(
        project_def_id=project_definition.id)

    response = await ac.post("/api/project_definition", data=project_definition.json())
    assert response.status_code == 200

    response = await ac.post("/api/project_definition_container", data=expected_project_definition_container.json())
    assert response.status_code == 200

    response = await ac.get(f"/api/project_definition_container/{expected_project_definition_container.id}")
    assert response.status_code == 200

    actual = unwrap(response, ProjectDefinitionContainerDto)
    assert actual == expected_project_definition_container

    response = await ac.delete(f"/api/project_definition_container/{expected_project_definition_container.id}")
    assert response.status_code == 200

    response = await ac.get(f"/api/project_definition_container/{expected_project_definition_container.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_given_translation_should_be_able_to_create_update_delete(ac):
    project_definition = ProjectDefinitionDtoFactory()
    translation = TranslationDtoFactory(ressource_id=project_definition.id)

    response = await ac.post("/api/project_definition", data=project_definition.json())
    assert response.status_code == 200

    response = await ac.post("/api/translation", data=translation.json())
    assert response.status_code == 200

    response = await ac.get(f"/api/translation/{translation.ressource_id}/{translation.locale}/{translation.name}")
    assert response.status_code == 200

    actual = unwrap(response, TranslationDto)
    assert actual == translation

    response = await ac.delete(f"/api/translation/{translation.ressource_id}/{translation.locale}/{translation.name}")
    assert response.status_code == 200

    response = await ac.get(f"/api/translation/{translation.ressource_id}/{translation.locale}/{translation.name}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_given_translation_should_be_able_to_retrieve_it(ac, dal):
    ressource_id = uuid4()
    translations = dict(
        a_fr=TranslationDao(ressource_id=ressource_id, locale='fr',
                            name='a', value='a_fr'),
        a_en=TranslationDao(ressource_id=ressource_id, locale='en',
                            name='a', value='a_en'),
        b_fr=TranslationDao(ressource_id=ressource_id, locale='fr',
                            name='b', value='b_fr')
    )

    expected_translations = [translations['a_fr'], translations['b_fr']]
    await populate_db(dal, translation_table, translations)

    response = await ac.get(f"/api/translation/{ressource_id}/fr")
    assert response.status_code == 200

    actual = unwrap_many(response, TranslationDto, lambda x: x.name)
    assert actual == expected_translations
