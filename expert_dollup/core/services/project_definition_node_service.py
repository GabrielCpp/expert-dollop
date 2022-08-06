from abc import abstractmethod
from uuid import UUID
from typing import Optional, List, Dict
from expert_dollup.shared.database_services import CollectionService
from expert_dollup.core.domains import ProjectDefinitionNode


class ProjectDefinitionNodeService(CollectionService[ProjectDefinitionNode]):
    @abstractmethod
    async def get_fields_id_by_name(
        self, project_definition_id: UUID, names: Optional[List[str]] = None
    ) -> Dict[str, UUID]:
        pass

    @abstractmethod
    async def has_path(self, path: List[UUID]) -> bool:
        pass

    @abstractmethod
    async def delete_child_of(self, id: UUID):
        pass

    @abstractmethod
    async def find_children(
        self, project_definition_id: UUID, path: List[UUID]
    ) -> List[ProjectDefinitionNode]:
        pass

    @abstractmethod
    async def find_root_sections(
        self, project_definition_id: UUID
    ) -> List[ProjectDefinitionNode]:
        pass

    @abstractmethod
    async def find_root_section_nodes(
        self, project_definition_id: UUID, root_section_id: UUID
    ) -> List[ProjectDefinitionNode]:
        pass

    @abstractmethod
    async def find_form_content(
        self, project_definition_id: UUID, form_id: UUID
    ) -> List[ProjectDefinitionNode]:
        pass
