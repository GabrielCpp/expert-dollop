from abc import abstractmethod
from uuid import UUID
from typing import List
from expert_dollup.shared.database_services import Repository
from expert_dollup.core.domains import ProjectNodeMeta, ProjectDefinitionNode


class ProjectNodeMetaRepository(Repository[ProjectNodeMeta]):
    @abstractmethod
    async def find_project_defs(self, project_id: UUID) -> List[ProjectDefinitionNode]:
        pass

    @abstractmethod
    async def find_root_sections(self, project_id: UUID) -> List[ProjectNodeMeta]:
        pass

    @abstractmethod
    async def find_root_section_nodes(
        self, project_id: UUID, root_section_def_id: UUID
    ) -> List[ProjectNodeMeta]:
        pass

    @abstractmethod
    async def find_form_content(
        self, project_id: UUID, form_def_id: UUID
    ) -> List[ProjectNodeMeta]:
        pass
