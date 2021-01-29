from injector import Binder, inject
from expert_dollup.shared.starlette_injection import factory_of
from expert_dollup.infra.services import *
from expert_dollup.infra.expert_dollup_db import ExpertDollupDatabase
from expert_dollup.infra.services import ProjectDefinitionValueTypeService


def bind_services(binder: Binder) -> None:
    services = [
        ProjectDefinitionService,
        ProjectDefinitionContainerService,
        ProjectDefinitionValueTypeService,
        ProjectService,
        RessourceService,
        TranslationService,
        ProjectContainerService,
        ProjectContainerMetaService,
    ]

    for service in services:
        binder.bind(service, factory_of(service, database=ExpertDollupDatabase))
