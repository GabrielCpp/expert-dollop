from injector import Binder, inject
from predykt.shared.starlette_injection import factory_of
from predykt.infra.services import ProjectDefinitionService, ProjectDefinitionContainerService
from predykt.infra.predykt_db import PredyktDatabase


def bind_services(binder: Binder) -> None:
    binder.bind(ProjectDefinitionService, factory_of(
        ProjectDefinitionService, database=PredyktDatabase))
    binder.bind(ProjectDefinitionContainerService, factory_of(
        ProjectDefinitionContainerService, database=PredyktDatabase))
