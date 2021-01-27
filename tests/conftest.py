import pytest
import os
import logging
import os
from injector import Injector
from dotenv import load_dotenv
from pathlib import Path
from async_asgi_testclient import TestClient
from expert_dollup.infra.expert_dollup_db import ExpertDollupDatabase
from expert_dollup.app.app import creat_app
from expert_dollup.app.modules import build_container
from .fixtures import init_db, load_fixture, ExpertDollupDbFixture

load_dotenv(dotenv_path=Path(".") / ".env.test")


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

    force_rollback = os.getenv("FORCE_ROLLBACK", True) is True
    database = ExpertDollupDatabase(DATABASE_URL, force_rollback=force_rollback)

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
    fixture = load_fixture(ExpertDollupDbFixture.SimpleProject)
    await init_db(dal, fixture)
    yield fixture
