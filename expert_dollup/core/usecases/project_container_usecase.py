from typing import Awaitable, List, Optional
from uuid import UUID, uuid4
from collections import defaultdict
from expert_dollup.core.exceptions import RessourceNotFound
from expert_dollup.core.domains import (
    ProjectContainer,
    ProjectContainerTree,
    ProjectContainerFilter,
    ProjectDefinitionNodeFilter,
    ProjectContainerNode,
    ValueUnion,
)
from expert_dollup.infra.services import (
    ProjectService,
    ProjectContainerService,
    ProjectDefinitionNodeService,
)
from expert_dollup.infra.validators import ProjectDefinitionValueTypeValidator
from expert_dollup.shared.database_services import Page


class ProjectContainerUseCase:
    def __init__(
        self,
        project_service: ProjectService,
        project_container_service: ProjectContainerService,
        project_definition_node_service: ProjectDefinitionNodeService,
        project_definition_value_type_validator: ProjectDefinitionValueTypeValidator,
    ):
        self.project_service = project_service
        self.project_container_service = project_container_service
        self.project_definition_node_service = project_definition_node_service
        self.project_definition_value_type_validator = (
            project_definition_value_type_validator
        )

    async def find_subtree(
        self, project_id: UUID, container_id: UUID
    ) -> Awaitable[ProjectContainerTree]:
        container = await self.project_container_service.find_one_by(
            ProjectContainerFilter(project_id=project_id, id=container_id)
        )
        subtree = await self.project_container_service.find_subtree(container)
        return subtree

    async def find_by_type(
        self, project_id: UUID, type_id: UUID
    ) -> Awaitable[List[ProjectContainer]]:
        results = await self.project_container_service.find_by(
            ProjectContainerFilter(project_id=project_id, type_id=type_id)
        )

        return Page(limit=len(results), results=results, next_page_token=None)

    async def find_by_id(self, id: UUID) -> Awaitable[ProjectContainer]:
        container = await self.project_container_service.find_by_id(id)
        return container

    async def find_by_path(
        self, project_id: UUID, path: List[UUID], level: Optional[int]
    ) -> Awaitable[ProjectContainerTree]:
        return await self.project_container_service.find_children_tree(
            project_id, path, level
        )

    async def update_container_value(
        self, project_id: UUID, container_id: UUID, value: ValueUnion
    ):
        container = await self.project_container_service.find_one_by(
            ProjectContainerFilter(project_id=project_id, id=container_id)
        )

        definition_container = await self.project_definition_node_service.find_by_id(
            container.type_id
        )

        await self.project_definition_value_type_validator.validate_value(
            definition_container.value_type, definition_container.config, value
        )

        await self.project_container_service.update(
            ProjectContainerFilter(value=value),
            ProjectContainerFilter(project_id=project_id, id=container_id),
        )

    async def add_collection(
        self,
        project_id: UUID,
        collection_type_id: UUID,
        parent_container_id: Optional[UUID],
    ) -> Awaitable[ProjectContainerTree]:
        project = await self.project_service.find_by_id(project_id)
        collection_definition_container = (
            await self.project_definition_node_service.find_one_by(
                ProjectDefinitionNodeFilter(
                    project_def_id=project.project_def_id, id=collection_type_id
                )
            )
        )

        definition_containers = (
            await self.project_definition_node_service.find_children_tree(
                project.project_def_id, collection_definition_container.subpath
            )
        )

        parent_path = []

        if not parent_container_id is None:
            parent_container = await self.project_container_service.find_one_by(
                ProjectContainerFilter(project_id=project_id, id=parent_container_id)
            )

            parent_path = parent_container.subpath

        assert len(parent_path) == len(collection_definition_container.path)
        type_to_instance_id = defaultdict(
            uuid4,
            zip(
                collection_definition_container.path,
                parent_path,
            ),
        )

        project_containers = [
            ProjectContainer(
                id=type_to_instance_id[definition_container.id],
                project_id=project.id,
                type_id=definition_container.id,
                path=[
                    type_to_instance_id[def_id] for def_id in definition_container.path
                ],
                value=definition_container.default_value,
            )
            for definition_container in [
                collection_definition_container,
                *definition_containers,
            ]
        ]

        await self.project_container_service.insert_many(project_containers)
        subtree = await self.project_container_service.find_subtree(
            project_containers[0]
        )

        return subtree

    async def clone_collection(self, project_id: UUID, container_id: UUID):
        parent_container = await self.project_container_service.find_one_by(
            ProjectContainerFilter(project_id=project_id, id=container_id)
        )

        children = await self.project_container_service.find_children(
            project_id, parent_container.subpath
        )

        id_mapping = defaultdict(
            uuid4, [(item, item) for item in parent_container.path]
        )

        project_containers = [
            ProjectContainer(
                id=id_mapping[container_clone.id],
                project_id=container_clone.project_id,
                type_id=container_clone.type_id,
                path=[
                    id_mapping[container_id] for container_id in container_clone.path
                ],
                value=container_clone.value,
            )
            for container_clone in [
                parent_container,
                *children,
            ]
        ]

        await self.project_container_service.insert_many(project_containers)
        subtree = await self.project_container_service.find_subtree(
            project_containers[0]
        )

        return subtree

    async def remove_collection(
        self, project_id: UUID, container_id: UUID
    ) -> Awaitable:
        container = await self.project_container_service.find_one_by(
            ProjectContainerFilter(project_id=project_id, id=container_id)
        )
        await self.project_container_service.remove_collection(container)
