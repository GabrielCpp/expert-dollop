import expert_dollup.infra.services as services
import expert_dollup.infra.queries as queries
import expert_dollup.core.queries as core_queries
from os import environ
from inspect import isclass
from injector import Binder, singleton, inject
from expert_dollup.shared.starlette_injection import factory_of
from expert_dollup.infra.expert_dollup_db import ExpertDollupDatabase
import expert_dollup.infra.expert_dollup_db as daos
from expert_dollup.infra.validators import SchemaValidator
from expert_dollup.infra.providers import WordProvider
from expert_dollup.shared.database_services import create_connection


def bind_database(binder: Binder) -> None:
    DATABASE_URL = environ["DATABASE_URL"]
    database = create_connection(DATABASE_URL, daos)
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


def get_classes(m):
    return [class_type for class_type in m.__dict__.values() if isclass(class_type)]


def bind_queries(binder: Binder) -> None:
    for service_type in get_classes(services):
        binder.bind(
            core_queries.Plucker[service_type],
            factory_of(queries.PluckQuery, service=service_type),
        )


def bind_providers(binder: Binder) -> None:
    with open("./assets/corncob_lowercase.txt") as f:
        words = [word for word in f.readlines() if word != ""]

    binder.bind(WordProvider, to=WordProvider(words), scope=singleton)
