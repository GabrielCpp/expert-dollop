import pytest
import os
import logging
from injector import Injector
from dotenv import load_dotenv
from pathlib import Path
from async_asgi_testclient import TestClient
from expert_dollup.app.app import creat_app
from expert_dollup.app.modules import build_container
from expert_dollup.infra.expert_dollup_db import ExpertDollupDatabase
from expert_dollup.shared.database_services import DbConnection
import expert_dollup.infra.services as services
from expert_dollup.shared.automapping import Mapper
from expert_dollup.shared.database_services import create_connection
from .fixtures import *
from factory.random import reseed_random

load_dotenv(dotenv_path=Path(".") / ".env.test")
load_dotenv()
reseed_random(1)


@pytest.fixture
async def dal() -> DbConnection:
    DATABASE_URL = os.environ["DATABASE_URL"]
    force_rollback = os.getenv("FORCE_ROLLBACK", True) in [True, "True"]
    connection = create_connection(DATABASE_URL, force_rollback=False)

    await connection.truncate_db()
    await connection.connect()
    yield connection

    if connection.is_connected:
        await connection.disconnect()


@pytest.fixture
def container(dal: DbConnection, request) -> Injector:
    container = build_container()
    container.binder.bind(ExpertDollupDatabase, dal)

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
async def ac(app, caplog) -> TestClient:
    caplog.set_level(logging.ERROR)

    async with TestClient(app) as ac:
        yield ac
