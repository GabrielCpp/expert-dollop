from os import environ
from inspect import isclass
from injector import Binder, singleton, inject, Injector
from expert_dollup.infra.storage_connectors import (
    LocalStorage,
    GoogleCloudStorage,
    StorageProxy,
)
from expert_dollup.shared.starlette_injection import (
    factory_of,
    get_classes,
    get_base,
    get_arg,
    is_development,
    Constant,
)
from expert_dollup.shared.database_services import *
from expert_dollup.shared.automapping import Mapper
from expert_dollup.infra.expert_dollup_storage import ExpertDollupStorage
from expert_dollup.infra.expert_dollup_db import ExpertDollupDatabase
from expert_dollup.infra.ressource_auth_db import RessourceAuthDatabase
from expert_dollup.infra.validators import SchemaValidator
from expert_dollup.infra.providers import WordProvider
import expert_dollup.infra.services as services
import expert_dollup.infra.expert_dollup_db as expert_dollup_db_daos
import expert_dollup.infra.ressource_auth_db.daos as ressource_db_daos
import expert_dollup.infra.ressource_auth_db.services as ressource_auth_db_services
import expert_dollup.infra.storages as storages
import expert_dollup.infra.paginators as paginators
from expert_dollup.infra.storage_connectors import ObjectNotFound
from expert_dollup.core.exceptions import RessourceNotFound
from expert_dollup.infra.ressource_engine import RessourceEngine
from expert_dollup.core.utils import authorization_factory
from expert_dollup.core.domains import *
import expert_dollup.core.repositories as repositories
from expert_dollup.app.settings import load_app_settings

storage_exception_mappings = {ObjectNotFound: lambda e: RessourceNotFound()}


def bind_ressource_engines(binder: Binder) -> None:
    for ressource_type in authorization_factory.ressource_types:
        binder.bind(
            UserRessourcePaginator[ressource_type],
            factory_of(
                RessourceEngine[ressource_type],
                user_service=CollectionService[Ressource],
                ressource_service=CollectionService[Ressource],
                mapper=Mapper,
                domain_service=CollectionService[ressource_type],
            ),
        )


def bind_database_expert_dollup(binder: Binder) -> None:
    DATABASE_URL = environ["EXPERT_DOLLUP_DB_URL"]
    database = create_connection(DATABASE_URL, expert_dollup_db_daos)
    binder.bind(ExpertDollupDatabase, to=database, scope=singleton)


def bind_database_ressource(binder: Binder) -> None:
    DATABASE_URL = environ["AUTH_DB_URL"]
    database = create_connection(DATABASE_URL, ressource_db_daos)
    binder.bind(RessourceAuthDatabase, to=database, scope=singleton)


def bind_database_context(binder: Binder) -> None:
    binder.bind(
        DatabaseContext,
        to=factory_of(
            DatabaseContextMultiplexer,
            injector=Injector,
            databases=Constant([RessourceAuthDatabase, ExpertDollupDatabase]),
        ),
        scope=singleton,
    )


def bind_storage(binder: Binder) -> None:
    settings = load_app_settings()
    storage = StorageProxy(
        LocalStorage(settings.app_bucket_name)
        if is_development()
        else GoogleCloudStorage(settings.app_bucket_name),
        storage_exception_mappings,
    )
    binder.bind(ExpertDollupStorage, to=storage, scope=singleton)

    for class_type in get_classes(storages):
        core_class_type = get_base(class_type)
        binder.bind(core_class_type, inject(class_type))


def bind_services(binder: Binder) -> None:
    for class_type in get_classes(ressource_auth_db_services):
        domain = get_arg(get_base(class_type))
        binder.bind(
            CollectionService[domain],
            factory_of(class_type, database=RessourceAuthDatabase, mapper=Mapper),
        )

    for class_type in get_classes(services):
        domain = get_arg(get_base(class_type))
        binder.bind(
            CollectionService[domain],
            factory_of(class_type, database=ExpertDollupDatabase, mapper=Mapper),
        )

    for class_type in get_classes(services):
        domain = get_arg(get_base(class_type))

        for repo_type in get_classes(repositories):
            repo_domain = get_arg(get_base(repo_type))

            if domain is repo_domain:
                binder.bind(
                    repo_type,
                    factory_of(
                        class_type, database=ExpertDollupDatabase, mapper=Mapper
                    ),
                )
                break


def bind_validators(binder: Binder) -> None:
    binder.bind(
        SchemaValidator,
        inject(SchemaValidator),
    )


def bind_queries(binder: Binder) -> None:
    service_by_domain = {
        get_arg(get_base(service_type)): service_type
        for service_type in get_classes(services)
    }

    for domain_type in service_by_domain.keys():
        binder.bind(
            Plucker[domain_type],
            factory_of(
                PluckQuery[domain_type],
                service=CollectionService[domain_type],
                mapper=Mapper,
            ),
        )


def bind_paginators(binder: Binder) -> None:
    service_by_domain = {
        get_arg(get_base(service_type)): service_type
        for service_type in get_classes(services)
    }

    for paginator_type in get_classes(paginators):
        domain_type = get_arg(get_base(paginator_type))
        assert domain_type in service_by_domain, f"domain_type: {domain_type}"

        binder.bind(
            Paginator[domain_type],
            factory_of(paginator_type, service=CollectionService[domain_type]),
        )


def bind_providers(binder: Binder) -> None:
    with open("./assets/corncob_lowercase.txt") as f:
        words = [word for word in f.readlines() if word != ""]

    binder.bind(WordProvider, to=WordProvider(words), scope=singleton)
