from os import environ
from typing import Union
from expert_dollup.shared.starlette_injection import *
from expert_dollup.shared.database_services import *
from expert_dollup.shared.automapping import *
from expert_dollup.infra.expert_dollup_storage import ExpertDollupStorage
from expert_dollup.infra.expert_dollup_db import ExpertDollupDatabase
from expert_dollup.infra.ressource_auth_db import RessourceAuthDatabase
from expert_dollup.infra.validators import SchemaValidator
from expert_dollup.infra.providers import WordProvider
from expert_dollup.infra.ressource_engine import RessourceEngine
from expert_dollup.core.utils import authorization_factory
from expert_dollup.core.domains import *
from expert_dollup.core.exceptions import RessourceNotFound
from expert_dollup.app.settings import load_app_settings
from expert_dollup.infra.repositories import *
from expert_dollup.core.repositories import *
from ..definitions import (
    auth_metadatas,
    expert_dollup_metadatas,
    paginations,
    storage_metadatas,
)

storage_exception_mappings = {ObjectNotFound: lambda e: RessourceNotFound()}


def bind_ressource_engines(builder: InjectorBuilder) -> None:
    for ressource_type in authorization_factory.ressource_types:
        builder.add_factory(
            TypedInjection.make_type_name(UserRessourcePaginator, ressource_type),
            RessourceEngine,
            user_service=TypedInjection.make_type_name(InternalRepository, Ressource),
            ressource_service=TypedInjection.make_type_name(
                InternalRepository, Ressource
            ),
            domain_service=TypedInjection.make_type_name(
                InternalRepository, ressource_type
            ),
            mapper=Mapper,
        )


def bind_database_expert_dollup(builder: InjectorBuilder) -> None:
    expert_dollup_db = create_connection(environ["EXPERT_DOLLUP_DB_URL"])
    expert_dollup_db.load_metadatas(expert_dollup_metadatas)
    builder.add_object(ExpertDollupDatabase, expert_dollup_db)


def bind_database_auth(builder: InjectorBuilder) -> None:
    auth_db = create_connection(environ["AUTH_DB_URL"])
    auth_db.load_metadatas(auth_metadatas)
    builder.add_object(RessourceAuthDatabase, auth_db)


def bind_storage(builder: InjectorBuilder) -> None:
    blob_db = create_connection(environ["EXPERT_DOLLUP_STORAGE"])
    blob_db.load_metadatas(storage_metadatas)
    builder.add_object(ExpertDollupStorage, blob_db)


def bind_database_context(builder: InjectorBuilder) -> None:
    builder.add_singleton(
        DatabaseContext,
        DatabaseContextMultiplexer,
        injector=Injector,
        databases=InjectorBuilder.forward(
            [RessourceAuthDatabase, ExpertDollupDatabase]
        ),
    )


def bind_base_repositories(builder: InjectorBuilder) -> None:
    def get_repository(
        database: DbConnection, mapper: Mapper, metadata: RepositoryMetadata
    ):
        return database.get_collection_service(metadata, mapper)

    for metadata in expert_dollup_metadatas:
        builder.add_factory(
            TypedInjection.make_type_name(Repository, metadata.domain),
            get_repository,
            database=ExpertDollupDatabase,
            mapper=Mapper,
            metadata=InjectorBuilder.forward(metadata),
        )

        builder.add_factory(
            TypedInjection.make_type_name(InternalRepository, metadata.domain),
            get_repository,
            database=ExpertDollupDatabase,
            mapper=Mapper,
            metadata=InjectorBuilder.forward(metadata),
        )

    for metadata in auth_metadatas:
        builder.add_factory(
            TypedInjection.make_type_name(Repository, metadata.domain),
            get_repository,
            database=RessourceAuthDatabase,
            mapper=Mapper,
            metadata=InjectorBuilder.forward(metadata),
        )

        builder.add_factory(
            TypedInjection.make_type_name(InternalRepository, metadata.domain),
            get_repository,
            database=RessourceAuthDatabase,
            mapper=Mapper,
            metadata=InjectorBuilder.forward(metadata),
        )

    for metadata in storage_metadatas:
        builder.add_factory(
            TypedInjection.make_type_name(Repository, metadata.domain),
            get_repository,
            database=ExpertDollupStorage,
            mapper=Mapper,
            metadata=InjectorBuilder.forward(metadata),
        )

        builder.add_factory(
            TypedInjection.make_type_name(InternalRepository, metadata.domain),
            get_repository,
            database=ExpertDollupStorage,
            mapper=Mapper,
            metadata=InjectorBuilder.forward(metadata),
        )


def bind_custom_repositories(builder: InjectorBuilder) -> None:
    builder.add_factory(
        ProjectDefinitionNodeRepository,
        ProjectDefinitionNodeInternalRepository,
        repository=TypedInjection.make_type_name(
            InternalRepository, ProjectDefinitionNode
        ),
    )

    builder.add_factory(
        ProjectNodeMetaRepository,
        ProjectNodeMetaInternalRepository,
        repository=TypedInjection.make_type_name(InternalRepository, ProjectNodeMeta),
    )

    builder.add_factory(
        ProjectNodeRepository,
        ProjectNodeInternalRepository,
        repository=TypedInjection.make_type_name(InternalRepository, ProjectNode),
    )

    builder.add_factory(
        FormulaRepository,
        FormulaInternalRepository,
        repository=TypedInjection.make_type_name(InternalRepository, Formula),
    )

    builder.add_factory(
        DefinitionNodeFormulaRepository,
        DefinitionNodeFormulaInternalRepository,
        repository=TypedInjection.make_type_name(
            InternalRepository, Union[ProjectDefinitionNode, Formula]
        ),
    )

    builder.add_factory(
        DatasheetElementRepository,
        DatasheetElementInternalRepository,
        repository=TypedInjection.make_type_name(InternalRepository, DatasheetElement),
        mapper=Mapper,
    )


def bind_validators(builder: InjectorBuilder) -> None:
    builder.add_singleton(SchemaValidator, SchemaValidator)


def bind_paginators(builder: InjectorBuilder) -> None:
    for pagination_details in paginations:
        builder.add_factory(
            TypedInjection.make_type_name(Paginator, pagination_details.for_domain),
            CollectionPaginator,
            repository=TypedInjection.make_type_name(
                Repository, pagination_details.for_domain
            ),
            mapper=Mapper,
            pagination_details=InjectorBuilder.forward(pagination_details),
        )


def bind_providers(builder: InjectorBuilder) -> None:
    with open("./assets/corncob_lowercase.txt") as f:
        words = [word for word in f.readlines() if word != ""]

    builder.add_singleton(
        WordProvider, WordProvider, words=InjectorBuilder.forward(words)
    )


def bind_io_modules(builder: InjectorBuilder) -> None:
    bind_database_expert_dollup(builder)
    bind_database_auth(builder)
    bind_storage(builder)
    bind_base_repositories(builder)
    bind_custom_repositories(builder)
    bind_database_context(builder)
    bind_providers(builder)
    bind_validators(builder)
    bind_ressource_engines(builder)
    bind_paginators(builder)
