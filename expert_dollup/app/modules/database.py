import os
from injector import Binder, singleton
from expert_dollup.infra.expert_dollup_db import ExpertDollupDatabase


def bind_database(binder: Binder) -> None:
    DATABASE_URL = "postgres://{}:{}@{}/{}".format(
        os.environ["POSTGRES_USERNAME"],
        os.environ["POSTGRES_PASSWORD"],
        os.environ["POSTGRES_HOST"],
        os.environ["POSTGRES_DB"]
    )

    database = ExpertDollupDatabase(DATABASE_URL)
    binder.bind(ExpertDollupDatabase, to=database, scope=singleton)
