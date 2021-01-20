from injector import Binder, inject
from expert_dollup.shared.starlette_injection import factory_of
from expert_dollup.infra.services import (
    ProjectDefinitionService,
    ProjectDefinitionContainerService,
    TranslationService,
    ProjectService,
    RessourceService,
    ProjectDefinitionPluginService,
)
from expert_dollup.infra.expert_dollup_db import ExpertDollupDatabase


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
        binder.bind(service, factory_of(service, database=ExpertDollupDatabase))
