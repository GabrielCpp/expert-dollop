from abc import abstractmethod
from uuid import UUID
from typing import List, Optional
from expert_dollup.shared.database_services import Repository
from expert_dollup.core.domains import ProjectNode


class ProjectNodeRepository(Repository[ProjectNode]):
    @abstractmethod
    async def find_children(
        self, project_id: UUID, path: List[UUID], level: Optional[int] = None
    ) -> List[ProjectNode]:
        pass

    @abstractmethod
    async def remove_collection(self, container: ProjectNode) -> None:
        pass

    @abstractmethod
    async def find_root_sections(self, project_id: UUID) -> List[ProjectNode]:
        pass

    @abstractmethod
    async def find_root_section_nodes(
        self, project_id: UUID, root_section_id: UUID
    ) -> List[ProjectNode]:
        pass

    @abstractmethod
    async def find_form_content(
        self, project_id: UUID, form_id: UUID
    ) -> List[ProjectNode]:
        pass

    @abstractmethod
    async def get_all_fields(self, project_id: UUID) -> List[ProjectNode]:
        pass

    @abstractmethod
    async def find_node_on_path_by_type(
        self, project_id: UUID, start_with_path: List[UUID], type_id: UUID
    ) -> List[ProjectNode]:
        pass
