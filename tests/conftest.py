import pytest
import faker
import logging
from uuid import UUID
from dotenv import load_dotenv
from factory.random import reseed_random
from factory import Faker
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


class UniqueNameIdProvider(faker.providers.BaseProvider):
    def unique_name_id(self) -> UUID:
        hexs = self.hexify("^" * 32)
        return "n" + hexs


class WordStringProvider(faker.providers.lorem.Provider):
    def words_str(self) -> UUID:
        return " ".join(self.words())


class UnderscoredNameProvider(faker.providers.lorem.Provider):
    def underscored_name(self) -> UUID:
        return " ".join(self.words())


load_dotenv(".env")
reseed_random(1)
Faker.add_provider(PyUUIDProvider)
Faker.add_provider(UniqueNameIdProvider)
Faker.add_provider(DateTimeProvider)
Faker.add_provider(WordStringProvider)
Faker.add_provider(UnderscoredNameProvider)


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


@pytest.fixture
async def ac(
    app, container: Injector, db_helper: DbFixtureHelper, caplog
) -> IntegratedTestClient:
    caplog.set_level(logging.ERROR)
    auth_service = container.get(AuthService)
    user_service = container.get(Repository[User])

    async with IntegratedTestClient(app, auth_service, user_service, db_helper) as ac:
        yield ac


@pytest.fixture
def logger_factory(container, logger_observer):
    return container.get(LoggerFactory)
