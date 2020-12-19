import os
from injector import Binder, singleton
from predykt.infra.predykt_db import PredyktDatabase


def bind_database(binder: Binder) -> None:
    DATABASE_URL = "postgres://{}:{}@{}/{}".format(
        os.environ["POSTGRES_USERNAME"],
        os.environ["POSTGRES_PASSWORD"],
        os.environ["POSTGRES_HOST"],
        os.environ["POSTGRES_DB"]
    )

    database = PredyktDatabase(DATABASE_URL)
    binder.bind(PredyktDatabase, to=database, scope=singleton)
