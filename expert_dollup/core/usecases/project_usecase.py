import structlog
from typing import Awaitable
from collections import deque
from uuid import UUID, uuid4
from collections import defaultdict
from expert_dollup.core.exceptions import RessourceNotFound, ValidationError
from expert_dollup.core.domains import (
    Project,
    ProjectContainer,
    ProjectContainerMeta,
    ProjectDefinitionContainerFilter,
    ProjectContainerFilter,
    ProjectContainerMetaFilter,
)
from expert_dollup.core.builders import RessourceBuilder
from expert_dollup.infra.services import (
    ProjectService,
    RessourceService,
    ProjectDefinitionService,
    ProjectDefinitionContainerService,
    ProjectContainerService,
    ProjectContainerMetaService,
)

logger = structlog.get_logger(__name__)


class ProjectUseCase:
    def __init__(
        self,
        service: ProjectService,
        project_container_service: ProjectContainerService,
        project_container_meta_service: ProjectContainerMetaService,
        ressource_service: RessourceService,
        project_definition_service: ProjectDefinitionService,
        project_definition_container_service: ProjectDefinitionContainerService,
        ressource_builder: RessourceBuilder,
    ):
        self.service = service
        self.project_container_service = project_container_service
        self.project_container_meta_service = project_container_meta_service
        self.project_definition_service = project_definition_service
        self.project_definition_container_service = project_definition_container_service
        self.ressource_builder = ressource_builder
        self.ressource_service = ressource_service

    async def add(self, domain: Project) -> Awaitable[Project]:
        ressource = self.ressource_builder.build(domain.id, domain.id, "project")

        await self._ensure_project_valid(domain)
        await self.ressource_service.insert(ressource)
        await self.service.insert(domain)
        await self._create_container_from_project_definition(domain)
        return await self.find_by_id(domain.id)

    async def clone(self, project_id: UUID) -> Awaitable[Project]:
        project = await self.find_by_id(project_id)
        cloned_project = Project(
            id=uuid4(),
            name=project.name,
            is_staged=False,
            project_def_id=project.project_def_id,
            datasheet_id=project.datasheet_id,
        )

        ressource = self.ressource_builder.build(
            cloned_project.id, cloned_project.id, "project"
        )
        await self.ressource_service.insert(ressource)
        await self.service.insert(cloned_project)

        containers = await self.project_container_service.find_by(
            ProjectContainerFilter(project_id=project_id)
        )

        id_mapping = defaultdict(uuid4)
        project_containers = [
            ProjectContainer(
                id=id_mapping[container.id],
                project_id=cloned_project.id,
                type_id=container.type_id,
                path=[id_mapping[container_id] for container_id in container.path],
                value=container.value,
            )
            for container in containers
        ]

        await self.project_container_service.insert_many(project_containers)

        container_metas = await self.project_container_meta_service.find_by(
            ProjectContainerMetaFilter(project_id=project_id)
        )

        project_container_metas = [
            ProjectContainerMeta(
                project_id=cloned_project.id,
                type_id=container_meta.type_id,
                state=container_meta.state,
            )
            for container_meta in container_metas
        ]

        await self.project_container_meta_service.insert_many(project_container_metas)

        return cloned_project

    async def remove_by_id(self, id: UUID) -> Awaitable:
        await self.project_container_service.remove_by(
            ProjectContainerFilter(project_id=project_id)
        )
        await self.service.delete_by_id(id)
        await self.ressource_service.delete_by_id(id)

    async def find_by_id(self, id: UUID) -> Awaitable[Project]:
        result = await self.service.find_by_id(id)
        return result

    async def _ensure_project_valid(self, project: Project):
        if not await self.project_definition_service.has(project.project_def_id):
            raise ValidationError.for_field("project_def_id", "Project does not exists")

    async def _create_container_from_project_definition(self, project: Project):
        project_containers = []
        project_container_metas = []
        type_to_instance_id = defaultdict(uuid4)
        container_definitions = await self.project_definition_container_service.find_by(
            ProjectDefinitionContainerFilter(project_def_id=project.project_def_id)
        )

        children_to_skip = set()

        for container_definition in sorted(container_definitions, key=lambda d: d.path):
            container_meta = ProjectContainerMeta(
                project_id=project.id,
                type_id=container_definition.id,
                state={},
            )

            project_container_metas.append(container_meta)

            if any(item in children_to_skip for item in container_definition.path):
                continue

            if container_definition.instanciate_by_default == False:
                children_to_skip.add(container_definition.id)
                continue

            container_id = type_to_instance_id[container_definition.id]
            container = ProjectContainer(
                id=container_id,
                project_id=project.id,
                type_id=container_definition.id,
                path=[
                    type_to_instance_id[def_id] for def_id in container_definition.path
                ],
                value=container_definition.default_value,
            )

            project_containers.append(container)

        await self.project_container_service.insert_many(project_containers)
        await self.project_container_meta_service.insert_many(project_container_metas)
