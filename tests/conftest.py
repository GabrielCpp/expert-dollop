import pytest
import faker
import logging
from uuid import UUID
from dotenv import load_dotenv
from factory.random import reseed_random
from factory import Faker
from async_asgi_testclient import TestClient
from expert_dollup.app.app import creat_app
from expert_dollup.app.modules import build_container
from expert_dollup.infra.expert_dollup_db import ExpertDollupDatabase
from expert_dollup.infra.ressource_auth_db import RessourceAuthDatabase
from expert_dollup.shared.automapping import Mapper
from expert_dollup.shared.database_services import *
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.domains import *
from .fixtures.injector_override.mock_services import logger_observer
from .fixtures import *


class DateTimeProvider(faker.providers.date_time.Provider):
    def date_time_s(self, tzinfo=None, end_datetime=None):
        return self.date_time(tzinfo, end_datetime).replace(microsecond=0)


class PyUUIDProvider(faker.providers.BaseProvider):
    def pyuuid4(self) -> UUID:
        hexs = self.hexify("^" * 32)
        return UUID(hexs)


class WordStringProvider(faker.providers.lorem.Provider):
    def words_str(self) -> UUID:
        return " ".join(self.words())


load_dotenv(".env")
reseed_random(1)
Faker.add_provider(PyUUIDProvider)
Faker.add_provider(DateTimeProvider)
Faker.add_provider(WordStringProvider)


@pytest.fixture
def container(request) -> Injector:
    container = build_container()

    other_bindings = get_overrides_for(request.function)
    for load_binding in other_bindings:
        load_binding(container)

    return container


@pytest.fixture
async def auth_dal(container: Injector) -> DbConnection:
    connection = container.get(RessourceAuthDatabase)

    await connection.connect()
    yield connection

    if connection.is_connected:
        await connection.disconnect()


@pytest.fixture
async def expert_dollup_dal(container: Injector) -> DbConnection:
    connection = container.get(ExpertDollupDatabase)

    await connection.connect()
    yield connection

    if connection.is_connected:
        await connection.disconnect()


@pytest.fixture
def db_helper(
    container: Injector, expert_dollup_dal: DbConnection, auth_dal: DbConnection
) -> DbFixtureHelper:
    return DbFixtureHelper(container, expert_dollup_dal, auth_dal)


@pytest.fixture
def mapper(container: Injector):
    mapper = container.get(Mapper)
    return mapper


@pytest.fixture
def app(container: Injector):
    return creat_app(container)


from pydantic import BaseModel, parse_obj_as
from async_asgi_testclient.response import Response as ClientResponse
from typing import Optional, Type, Callable, List


class IntegratedTestClient(TestClient):
    def __init__(
        self,
        app,
        auth_service: AuthService,
        user_service: Repository[User],
        db_helper: DbFixtureHelper,
    ):
        TestClient.__init__(self, app)
        self.auth_service = auth_service
        self.db_helper = db_helper
        self.user_service = user_service
        self.json_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def login(self, user: User):
        token = self.auth_service.make_token(user.oauth_id)
        self.headers.update({"Authorization": f"Bearer {token}"})

    async def login_super_user(self):
        if self.db_helper.db is None:
            await self.db_helper.load_fixtures(SuperUser())

        user = self.db_helper.db.get_only_one_matching(
            User, lambda u: u.oauth_id == SuperUser.oauth_id
        )

        if user is None:
            raise Exception("You must load SuperUser fixture")

        self.login(user)

    async def post_json(
        self,
        url: str,
        data: Optional[BaseModel] = None,
        expected_status_code: int = 200,
        unwrap_with: Optional[Type[BaseModel]] = None,
        after: Optional[Callable[[BaseModel], None]] = None,
    ):
        params = self._json_request_params(data)
        response = await self.post(url, **params)
        assert response.status_code == expected_status_code, response.text
        return self._convert_response(response, unwrap_with, after)

    async def put_json(
        self,
        url: str,
        data: Optional[BaseModel] = None,
        expected_status_code: int = 200,
        unwrap_with: Optional[Type[BaseModel]] = None,
        after: Optional[Callable[[BaseModel], None]] = None,
    ):
        params = self._json_request_params(data)
        response = await self.put(url, **params)
        assert response.status_code == expected_status_code, response.text
        return self._convert_response(response, unwrap_with, after)

    async def patch_json(
        self,
        url: str,
        data: Optional[BaseModel] = None,
        expected_status_code: int = 200,
        unwrap_with: Optional[Type[BaseModel]] = None,
        after: Optional[Callable[[BaseModel], None]] = None,
    ):
        params = self._json_request_params(data)
        response = await self.patch(url, **params)
        assert response.status_code == expected_status_code, response.text
        return self._convert_response(response, unwrap_with, after)

    async def get_json(
        self,
        url: str,
        expected_status_code: int = 200,
        unwrap_with: Optional[Type[BaseModel]] = None,
        after: Optional[Callable[[BaseModel], None]] = None,
    ):
        response = await self.get(url, headers=self.json_headers)
        assert response.status_code == expected_status_code, response.text
        return self._convert_response(response, unwrap_with, after)

    async def delete_json(
        self,
        url: str,
        expected_status_code: int = 200,
        unwrap_with: Optional[Type[BaseModel]] = None,
        after: Optional[Callable[[BaseModel], None]] = None,
    ):
        response = await self.delete(url, headers=self.json_headers)
        assert response.status_code == expected_status_code, response.text
        return self._convert_response(response, unwrap_with, after)

    def _convert_response(
        self,
        response,
        unwrap_with,
        after: Optional[Callable[[BaseModel], None]] = None,
    ):
        if unwrap_with is None:
            return response

        result = parse_obj_as(unwrap_with, response.json())

        if callable(after):
            after(result)

        return result

    def _json_request_params(
        self,
        data: Optional[BaseModel] = None,
    ) -> dict:
        params = dict(headers=self.json_headers)

        if not data is None:
            params["data"] = jsonify(data)

        return params


@pytest.fixture
async def ac(
    app, container: Injector, db_helper: DbFixtureHelper, caplog
) -> TestClient:
    caplog.set_level(logging.ERROR)
    auth_service = container.get(AuthService)
    user_service = container.get(Repository[User])

    async with IntegratedTestClient(app, auth_service, user_service, db_helper) as ac:
        yield ac


@pytest.fixture
def logger_factory(container, logger_observer):
    return container.get(LoggerFactory)
