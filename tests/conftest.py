import pytest
import os
import logging
import expert_dollup.infra.expert_dollup_db as expert_dollup_db_daos
import expert_dollup.infra.ressource_auth_db.daos as ressource_auth_db_daos
import expert_dollup.infra.services as services
from uuid import UUID
from injector import Injector
from dotenv import load_dotenv
from pathlib import Path
from factory.random import reseed_random
from factory import Faker
from faker.providers import BaseProvider
from async_asgi_testclient import TestClient
from expert_dollup.app.app import creat_app
from expert_dollup.app.modules import build_container
from expert_dollup.infra.expert_dollup_db import ExpertDollupDatabase
from expert_dollup.infra.ressource_auth_db import RessourceAuthDatabase
from expert_dollup.shared.automapping import Mapper
from expert_dollup.shared.database_services import (
    create_connection,
    DbConnection,
    CollectionService,
)
from expert_dollup.shared.starlette_injection import LoggerFactory, AuthService
from expert_dollup.core.domains import *
from .fixtures.injector_override.mock_services import logger_observer
from .fixtures import *
from faker.providers.date_time import Provider


class DateTimeProvider(Provider):
    def date_time_s(self, tzinfo=None, end_datetime=None):
        return self.date_time(tzinfo, end_datetime).replace(microsecond=0)


class PyProvider(BaseProvider):
    def pyuuid4(self) -> UUID:
        hexs = self.hexify("^" * 32)
        return UUID(hexs)


load_dotenv(dotenv_path=Path(".") / ".env.test")
load_dotenv()
reseed_random(1)
Faker.add_provider(PyProvider)
Faker.add_provider(DateTimeProvider)


@pytest.fixture
async def auth_dal() -> DbConnection:
    DATABASE_URL = os.environ["AUTH_DB_URL"]
    connection = create_connection(DATABASE_URL, ressource_auth_db_daos)

    await connection.connect()
    await connection.truncate_db()
    yield connection

    if connection.is_connected:
        await connection.disconnect()


@pytest.fixture
async def dal() -> DbConnection:
    DATABASE_URL = os.environ["EXPERT_DOLLUP_DB_URL"]
    connection = create_connection(DATABASE_URL, expert_dollup_db_daos)

    await connection.connect()
    yield connection

    if connection.is_connected:
        await connection.disconnect()


@pytest.fixture
def container(dal: DbConnection, auth_dal: DbConnection, request) -> Injector:
    container = build_container()
    container.binder.bind(ExpertDollupDatabase, dal)
    container.binder.bind(RessourceAuthDatabase, auth_dal)

    other_bindings = get_overrides_for(request.function)
    for load_binding in other_bindings:
        load_binding(container)

    return container


@pytest.fixture
def db_helper(container: Injector, dal: DbConnection) -> DbFixtureHelper:
    return DbFixtureHelper(container, dal).load_services(services)


@pytest.fixture
def mapper(container: Injector):
    mapper = container.get(Mapper)
    return mapper


@pytest.fixture
def app(container: Injector):
    return creat_app(container)


@pytest.fixture
async def ac(app, container: Injector, caplog) -> TestClient:
    caplog.set_level(logging.ERROR)
    user_service = container.get(CollectionService[User])
    auth_service = container.get(AuthService)

    user = make_superuser()
    await user_service.upserts([user])
    token = auth_service.make_token(user.oauth_id)

    async with TestClient(app, headers={"Authorization": f"Bearer {token}"}) as ac:
        yield ac


@pytest.fixture
def logger_factory(container, logger_observer):
    return container.get(LoggerFactory)
