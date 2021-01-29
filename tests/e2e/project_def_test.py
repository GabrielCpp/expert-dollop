import pytest
from ..fixtures import (
    load_fixture,
    ExpertDollupDbFixture,
    map_dao_to_dto,
    normalize_request_results,
    normalize_dtos,
)
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *
from urllib.parse import urlencode


class AsyncCursor:
    @staticmethod
    async def all(ac, url: str, limit: int = 500, after=lambda d: d) -> list:
        cursor = AsyncCursor(ac, url, limit)
        data = []

        while await cursor.next():
            data.extend(cursor.data)

        return after(data)

    def __init__(self, ac, url: str, limit: int = 500):
        self.ac = ac
        self.url = url
        self.limit = limit
        self.next_page_token = None
        self.has_next_page = True
        self._data = []

    async def next(self) -> bool:
        has_next_page = self.has_next_page

        if has_next_page is True:
            parameters = {"limit": self.limit}
            if not self.next_page_token is None:
                parameters["nextPageToken"] = self.next_page_token

            response = await self.ac.get(f"{self.url}?{urlencode(parameters)}")
            body = response.json()

            if response.status_code != 200:
                raise Exception(body)

            self.next_page_token = body["nextPageToken"]
            self.limit = body["limit"]
            self._data = body["results"]
            self.has_next_page = len(self._data) == self.limit

        return has_next_page

    @property
    def data(self) -> list:
        return self._data


@pytest.mark.asyncio
async def test_project_creation(ac, map_dao_to_dto):
    db = load_fixture(ExpertDollupDbFixture.SimpleProject)

    assert len(db.project_definitions) == 1
    project_definition = db.project_definitions[0]

    response = await ac.post("/api/project_definition", data=project_definition.json())
    assert response.status_code == 200, response.json()

    project_definition_containers_dto = map_dao_to_dto(
        db.project_definition_containers,
        ProjectDefinitionContainerDao,
        ProjectDefinitionContainer,
        ProjectDefinitionContainerDto,
    )

    for project_definiton_container_dto in project_definition_containers_dto:
        response = await ac.post(
            "/api/project_definition_container",
            data=project_definiton_container_dto.json(),
        )
        assert response.status_code == 200, response.json()

    containers = await AsyncCursor.all(
        ac,
        f"/api/{project_definition.id}/project_definition_containers",
        after=normalize_request_results(ProjectDefinitionContainerDto, "id"),
    )

    expected_containers = normalize_dtos(project_definition_containers_dto, "id")

    assert len(containers) == len(project_definition_containers_dto)
    assert containers == expected_containers
