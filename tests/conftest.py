import pytest
import logging
import os
from injector import Injector
from async_asgi_testclient import TestClient
from expert_dollup.infra.expert_dollup_db import ExpertDollupDatabase
from expert_dollup.app.app import creat_app
from expert_dollup.app.modules import build_container
from .fixtures import init_db, load_fixture, expert_dollupDbFixture


@pytest.fixture
def container() -> Injector:
    return build_container()


@pytest.fixture
def app(container: Injector):
    return creat_app(container)


@pytest.fixture
async def dal():
    DATABASE_URL = "postgres://{}:{}@{}/{}".format(
        os.environ["POSTGRES_USERNAME"],
        os.environ["POSTGRES_PASSWORD"],
        os.environ["POSTGRES_HOST"],
        os.environ["POSTGRES_DB"],
    )

    database = ExpertDollupDatabase(DATABASE_URL, force_rollback=True)

    await database.connect()
    yield database
    await database.disconnect()


@pytest.fixture
async def ac(app, container, dal, caplog) -> TestClient:
    caplog.set_level(logging.ERROR)

    container.binder.bind(ExpertDollupDatabase, dal)

    async with TestClient(app) as ac:
        yield ac


@pytest.fixture
async def expert_dollup_simple_project(dal):
    fixture = load_fixture(expert_dollupDbFixture.SimpleProject)
    await init_db(dal, fixture)
    yield fixture
