import expert_dollup.infra.services as services
from os import environ
from inspect import isclass
from injector import Binder, singleton, inject
from expert_dollup.shared.starlette_injection import factory_of
from expert_dollup.infra.expert_dollup_db import ExpertDollupDatabase
from expert_dollup.infra.validators import SchemaValidator
from expert_dollup.infra.providers import WordProvider


def bind_database(binder: Binder) -> None:
    DATABASE_URL = "postgresql://{}:{}@{}/{}".format(
        environ["POSTGRES_USERNAME"],
        environ["POSTGRES_PASSWORD"],
        environ["POSTGRES_HOST"],
        environ["POSTGRES_DB"],
    )

    database = ExpertDollupDatabase(DATABASE_URL)
    binder.bind(ExpertDollupDatabase, to=database, scope=singleton)


def bind_services(binder: Binder) -> None:
    for class_type in services.__dict__.values():
        if isclass(class_type):
            binder.bind(
                class_type, factory_of(class_type, database=ExpertDollupDatabase)
            )


def bind_validators(binder: Binder) -> None:
    binder.bind(
        SchemaValidator,
        inject(SchemaValidator),
    )


def bind_providers(binder: Binder) -> None:
    with open("./assets/corncob_lowercase.txt") as f:
        words = [word for word in f.readlines() if word != ""]

    binder.bind(WordProvider, to=lambda: WordProvider(words), scope=singleton)
