from injector import Binder, inject
from predykt.shared.starlette_injection import factory_of
from predykt.infra.services import (
    ProjectDefinitionService, ProjectDefinitionContainerService, TranslationService,
    ProjectService, RessourceService, ProjectDefinitionPluginService
)
from predykt.infra.predykt_db import PredyktDatabase


def bind_services(binder: Binder) -> None:
    services = [
        ProjectDefinitionService,
        ProjectDefinitionContainerService,
        ProjectDefinitionPluginService,
        ProjectService,
        RessourceService,
        TranslationService,
    ]

    for service in services:
        binder.bind(service, factory_of(service, database=PredyktDatabase))
