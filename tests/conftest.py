import pytest
import logging
import os
from injector import Injector
from async_asgi_testclient import TestClient
from predykt.infra.predykt_db import PredyktDatabase
from predykt.app.app import creat_app
from predykt.app.modules import build_container


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
        os.environ["POSTGRES_DB"]
    )

    database = PredyktDatabase(DATABASE_URL, force_rollback=True)

    await database.connect()
    yield database
    await database.disconnect()


@pytest.fixture
async def ac(app, container, dal, caplog) -> TestClient:
    caplog.set_level(logging.ERROR)

    container.binder.bind(PredyktDatabase, dal)

    async with TestClient(app) as ac:
        yield ac
