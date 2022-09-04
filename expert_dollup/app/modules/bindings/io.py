from os import environ
from injector import *
from expert_dollup.shared.starlette_injection import *
from expert_dollup.shared.database_services import *
from expert_dollup.shared.automapping import *
from expert_dollup.infra.storage_connectors import *
from expert_dollup.infra.expert_dollup_storage import ExpertDollupStorage
from expert_dollup.infra.expert_dollup_db import ExpertDollupDatabase
from expert_dollup.infra.ressource_auth_db import RessourceAuthDatabase
from expert_dollup.infra.validators import SchemaValidator
from expert_dollup.infra.providers import WordProvider
from expert_dollup.infra.storage_connectors import ObjectNotFound
from expert_dollup.infra.ressource_engine import RessourceEngine
from expert_dollup.core.utils import authorization_factory
from expert_dollup.core.domains import *
from expert_dollup.core.exceptions import RessourceNotFound
from expert_dollup.app.settings import load_app_settings
import expert_dollup.infra.storages as storages
from expert_dollup.infra.repositories import *
from expert_dollup.core.repositories import *
from ..definitions import auth_metadatas, expert_dollup_metadatas, paginations

storage_exception_mappings = {ObjectNotFound: lambda e: RessourceNotFound()}


def bind_ressource_engines(binder: Binder) -> None:
    for ressource_type in authorization_factory.ressource_types:
        binder.bind(
            UserRessourcePaginator[ressource_type],
            factory_of(
                RessourceEngine[ressource_type],
                user_service=InternalRepository[Ressource],
                ressource_service=InternalRepository[Ressource],
                domain_service=InternalRepository[ressource_type],
                mapper=Mapper,
            ),
        )


def bind_database_expert_dollup(binder: Binder) -> None:
    expert_dollup_db = create_connection(environ["EXPERT_DOLLUP_DB_URL"])
    expert_dollup_db.load_metadatas(expert_dollup_metadatas)
    binder.bind(ExpertDollupDatabase, to=expert_dollup_db, scope=singleton)


def bind_database_ressource(binder: Binder) -> None:
    auth_db = create_connection(environ["AUTH_DB_URL"])
    auth_db.load_metadatas(auth_metadatas)
    binder.bind(RessourceAuthDatabase, to=auth_db, scope=singleton)


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


def bind_base_repositories(binder: Binder) -> None:
    def get_repository(
        database: DbConnection, mapper: Mapper, metadata: RepositoryMetadata
    ):
        return database.get_collection_service(metadata, mapper)

    for metadata in expert_dollup_metadatas:
        binder.bind(
            Repository[metadata.domain],
            factory_of(
                get_repository,
                database=ExpertDollupDatabase,
                mapper=Mapper,
                metadata=Constant(metadata),
            ),
        )

        binder.bind(
            InternalRepository[metadata.domain],
            factory_of(
                get_repository,
                database=ExpertDollupDatabase,
                mapper=Mapper,
                metadata=Constant(metadata),
            ),
        )

    for metadata in auth_metadatas:
        binder.bind(
            Repository[metadata.domain],
            factory_of(
                get_repository,
                database=RessourceAuthDatabase,
                mapper=Mapper,
                metadata=Constant(metadata),
            ),
        )

        binder.bind(
            InternalRepository[metadata.domain],
            factory_of(
                get_repository,
                database=RessourceAuthDatabase,
                mapper=Mapper,
                metadata=Constant(metadata),
            ),
        )


def bind_custom_repositories(binder: Binder) -> None:
    binder.bind(
        ProjectDefinitionNodeRepository,
        factory_of(
            ProjectDefinitionNodeInternalRepository,
            repository=InternalRepository[ProjectDefinitionNode],
        ),
    )
    binder.bind(
        ProjectNodeMetaRepository,
        factory_of(
            ProjectNodeMetaInternalRepository,
            repository=InternalRepository[ProjectNodeMeta],
        ),
    )
    binder.bind(
        ProjectNodeRepository,
        factory_of(
            ProjectNodeInternalRepository,
            repository=InternalRepository[ProjectNode],
        ),
    )
    binder.bind(
        FormulaRepository,
        factory_of(
            FormulaInternalRepository,
            repository=InternalRepository[Formula],
        ),
    )

    binder.bind(
        DefinitionNodeFormulaRepository,
        factory_of(
            DefinitionNodeFormulaInternalRepository,
            repository=InternalRepository[Union[ProjectDefinitionNode, Formula]],
        ),
    )


def bind_validators(binder: Binder) -> None:
    binder.bind(
        SchemaValidator,
        inject(SchemaValidator),
    )


def bind_queries(binder: Binder) -> None:
    for metadata in expert_dollup_metadatas:
        binder.bind(
            Plucker[metadata.domain],
            factory_of(
                PluckQuery[metadata.domain], repository=Repository[metadata.domain]
            ),
        )


def bind_paginators(binder: Binder) -> None:
    for pagination_details in paginations:
        binder.bind(
            Paginator[pagination_details.for_domain],
            factory_of(
                CollectionPaginator,
                repository=Repository[pagination_details.for_domain],
                mapper=Mapper,
                pagination_details=Constant(pagination_details),
            ),
        )


def bind_storages(binder: Binder) -> None:
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


def bind_providers(binder: Binder) -> None:
    with open("./assets/corncob_lowercase.txt") as f:
        words = [word for word in f.readlines() if word != ""]

    binder.bind(WordProvider, to=WordProvider(words), scope=singleton)


def bind_io_modules(binder: Binder) -> None:
    bind_ressource_engines(binder)
    bind_database_expert_dollup(binder)
    bind_database_ressource(binder)
    bind_database_context(binder)
    bind_base_repositories(binder)
    bind_custom_repositories(binder)
    bind_validators(binder)
    bind_queries(binder)
    bind_paginators(binder)
    bind_storages(binder)
    bind_providers(binder)
