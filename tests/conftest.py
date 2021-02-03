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
from dev.clean_db import truncate_db
from .fixtures import DbSetupHelper, ExpertDollupDbFixture

load_dotenv(dotenv_path=Path(".") / ".env.test")
load_dotenv()


@pytest.fixture
async def dal():
    truncate_db()
    DATABASE_URL = "postgresql://{}:{}@{}/{}".format(
        os.environ["POSTGRES_USERNAME"],
        os.environ["POSTGRES_PASSWORD"],
        os.environ["POSTGRES_HOST"],
        os.environ["POSTGRES_DB"],
    )

    force_rollback = os.getenv("FORCE_ROLLBACK", True) in [True, "True"]
    database = ExpertDollupDatabase(DATABASE_URL, force_rollback=False)

    await database.connect()
    yield database

    if database.is_connected:
        await database.disconnect()


@pytest.fixture
def container(dal) -> Injector:
    container = build_container()
    container.binder.bind(ExpertDollupDatabase, dal)
    return container


@pytest.fixture
def app(container: Injector):
    return creat_app(container)


@pytest.fixture
async def ac(app, caplog) -> TestClient:
    caplog.set_level(logging.ERROR)

    async with TestClient(app) as ac:
        yield ac


@pytest.fixture
async def expert_dollup_simple_project(container: Injector):
    db_helper = container.get(DbSetupHelper)
    fixture = DbSetupHelper.load_fixture(ExpertDollupDbFixture.SimpleProject)
    await db_helper.init_db(fixture)
    yield fixture
