from uuid import UUID
from predykt.core.domains.project_definition import ProjectDefinition
from predykt.core.exceptions import RessourceNotFound
from predykt.infra.services.project_definition_service import ProjectDefinitionService


class ProjectDefinitonUseCase:
    def __init__(self, project_definition_service: ProjectDefinitionService):
        self.project_definition_service = project_definition_service

    async def find_by_id(self, id: UUID) -> ProjectDefinition:
        result = await self.project_definition_service.find_by_id(id)

        if result is None:
            raise RessourceNotFound()

        return result
