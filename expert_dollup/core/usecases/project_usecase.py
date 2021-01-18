from typing import Awaitable
from collections import deque
from uuid import UUID, uuid4
from collections import defaultdict
from expert_dollup.core.exceptions import RessourceNotFound, ValidationError
from expert_dollup.core.domains import Project, ProjectContainer, ProjectContainerMeta
from expert_dollup.core.builders import RessourceBuilder
from expert_dollup.infra.services import (
    ProjectService,
    RessourceService,
    ProjectDefinitionService,
    ProjectDefinitionContainerService,
    ProjectContainerService,
    ProjectContainerMetaService,
)


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

    async def add(self, domain: Project) -> Awaitable:
        ressource = self.ressource_builder.build(domain.id, "project_")

        await self._ensure_project_valid(domain)
        await self.ressource_service.insert(ressource)
        await self.service.insert(domain)
        await self._create_container_from_porject_def(domain)
        return await self.find_by_id(domain.id)

    async def remove_by_id(self, id: UUID) -> Awaitable:
        await self.service.delete_by_id(id)
        await self.ressource_service.delete_by_id(id)

    async def update(self, domain: Project) -> Awaitable:
        await self._ensure_project_valid(domain)
        await self.service.update(domain)
        return await self.find_by_id(domain.id)

    async def find_by_id(self, id: UUID) -> Awaitable[Project]:
        result = await self.service.find_by_id(id)

        if result is None:
            raise RessourceNotFound()

        return result

    async def _ensure_project_valid(self, project: Project):
        if not await self.self.project_definition_service.has(project.project_def_id):
            raise ValidationError.for_field("project_def_id", "Project does not exists")

    async def _create_container_from_project_def(self, project: Project):
        project_containers = []
        project_container_metas
        type_to_instance_id = defaultdict(uuid4)
        container_definitions = (
            self.project_definition_container_service.all_from_project(
                roject.project_def_id
            )
        )

        async for container_definition in container_definitions:
            container_id = type_to_instance_id[container_definition.id]

            if container_definition.instanciate_by_default == True:
                container = ProjectContainer(
                    id=container_id,
                    project_id=project.id,
                    type_id=container_definition.id,
                    path=[
                        type_to_instance_id[def_id]
                        for def_id in container_definition.path
                    ],
                    value=container_definition.default_value,
                )

                project_containers.append(container)

            container_meta = ProjectContainerMeta(
                project_id=project.id,
                type_id=container_definition.id,
                custom_attributes=container_definition.custom_attributes,
            )

            project_container_metas.append(container_meta)

        await self.project_container_service.insert_many(project_containers)
        await self.project_container_meta_service.insert_many(project_container_metas)
